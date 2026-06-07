"""
Multi-threaded tile download engine.
Handles concurrent tile downloads with progress tracking, retry, and caching.
"""
import logging
import time
from pathlib import Path
from typing import List, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import hashlib

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

from PyQt6.QtCore import QObject, pyqtSignal

from app.core.models import TileInfo, DownloadProgress
from app.services.imagery_provider import ImageryProvider


@dataclass
class DownloadResult:
    """Result of a tile download attempt."""
    tile: TileInfo
    success: bool
    error_message: Optional[str] = None
    file_size: int = 0
    duration: float = 0.0


class TileDownloader(QObject):
    """
    Multi-threaded tile downloader with progress tracking.
    
    Signals:
        progress_updated: Emitted when download progress changes
        tile_downloaded: Emitted when a tile is successfully downloaded
        tile_failed: Emitted when a tile download fails
        download_completed: Emitted when all downloads complete
        download_error: Emitted on critical error
    """
    
    # Qt signals for progress updates
    progress_updated = pyqtSignal(DownloadProgress)
    tile_downloaded = pyqtSignal(TileInfo)
    tile_failed = pyqtSignal(TileInfo, str)
    download_completed = pyqtSignal(int, int)  # downloaded, failed
    download_error = pyqtSignal(str)
    
    def __init__(self, provider: ImageryProvider, cache_dir: Path, 
                 max_workers: int = 10, timeout: int = 30, max_retries: int = 3):
        """
        Initialize tile downloader.
        
        Args:
            provider: Imagery provider
            cache_dir: Directory for tile cache
            max_workers: Maximum concurrent downloads
            timeout: Download timeout in seconds
            max_retries: Maximum retry attempts per tile
        """
        super().__init__()
        
        self.provider = provider
        self.cache_dir = Path(cache_dir)
        self.max_workers = max_workers
        self.timeout = timeout
        self.max_retries = max_retries
        
        self.logger = logging.getLogger(__name__)
        
        # Create cache directory
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Download state
        self._cancelled = False
        self._session = None
        
        # Statistics
        self._start_time = 0
        self._total_bytes = 0
    
    def _get_session(self) -> 'requests.Session':
        """
        Get configured requests session with retry logic.
        
        Returns:
            Configured session
        """
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests library not available")
        
        if self._session is None:
            self._session = requests.Session()
            
            # Configure retry strategy
            retry_strategy = Retry(
                total=self.max_retries,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["GET"]
            )
            
            adapter = HTTPAdapter(max_retries=retry_strategy)
            self._session.mount("http://", adapter)
            self._session.mount("https://", adapter)
            
            # Set headers
            self._session.headers.update(self.provider.get_headers())
        
        return self._session
    
    def _get_cache_path(self, tile: TileInfo) -> Path:
        """
        Get cache file path for a tile.
        
        Args:
            tile: Tile info
            
        Returns:
            Path to cache file
        """
        # Create hash from provider name and tile coordinates
        cache_key = f"{self.provider.config.name}_{tile.z}_{tile.x}_{tile.y}"
        cache_hash = hashlib.md5(cache_key.encode()).hexdigest()
        
        # Organize by zoom level
        zoom_dir = self.cache_dir / str(tile.z)
        zoom_dir.mkdir(exist_ok=True)
        
        # Determine extension from URL
        url_lower = tile.url.lower()
        if '.png' in url_lower or 'format=image/png' in url_lower:
            ext = '.png'
        elif '.jpg' in url_lower or '.jpeg' in url_lower or 'format=image/jpeg' in url_lower:
            ext = '.jpg'
        else:
            ext = '.png'  # Default
        
        return zoom_dir / f"{cache_hash}{ext}"
    
    def _is_cached(self, tile: TileInfo) -> bool:
        """
        Check if tile is already cached.
        
        Args:
            tile: Tile info
            
        Returns:
            True if cached
        """
        cache_path = self._get_cache_path(tile)
        
        if cache_path.exists() and cache_path.stat().st_size > 0:
            tile.file_path = cache_path
            tile.downloaded = True
            return True
        
        return False
    
    def _download_tile(self, tile: TileInfo) -> DownloadResult:
        """
        Download a single tile.
        
        Args:
            tile: Tile info
            
        Returns:
            Download result
        """
        start_time = time.time()
        
        # Check if cancelled
        if self._cancelled:
            return DownloadResult(
                tile=tile,
                success=False,
                error_message="Download cancelled"
            )
        
        # Check cache first
        if self._is_cached(tile):
            self.logger.debug(f"Tile {tile.z}/{tile.x}/{tile.y} loaded from cache")
            return DownloadResult(
                tile=tile,
                success=True,
                duration=time.time() - start_time
            )
        
        # Download tile
        try:
            session = self._get_session()
            
            response = session.get(tile.url, timeout=self.timeout, stream=True)
            response.raise_for_status()
            
            # Save to cache
            cache_path = self._get_cache_path(tile)
            
            with open(cache_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if self._cancelled:
                        return DownloadResult(
                            tile=tile,
                            success=False,
                            error_message="Download cancelled"
                        )
                    f.write(chunk)
            
            file_size = cache_path.stat().st_size
            
            # Update tile info
            tile.file_path = cache_path
            tile.downloaded = True
            
            duration = time.time() - start_time
            
            self.logger.debug(
                f"Downloaded tile {tile.z}/{tile.x}/{tile.y} "
                f"({file_size} bytes in {duration:.2f}s)"
            )
            
            return DownloadResult(
                tile=tile,
                success=True,
                file_size=file_size,
                duration=duration
            )
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Failed to download tile {tile.z}/{tile.x}/{tile.y}: {error_msg}")
            
            return DownloadResult(
                tile=tile,
                success=False,
                error_message=error_msg,
                duration=time.time() - start_time
            )
    
    def download_tiles(self, tiles: List[TileInfo]):
        """
        Download multiple tiles concurrently.
        
        Args:
            tiles: List of tiles to download
        """
        if not tiles:
            self.logger.warning("No tiles to download")
            self.download_completed.emit(0, 0)
            return
        
        self.logger.info(f"Starting download of {len(tiles)} tiles with {self.max_workers} workers")
        
        # Reset state
        self._cancelled = False
        self._start_time = time.time()
        self._total_bytes = 0
        
        downloaded_count = 0
        failed_count = 0
        
        # Create progress tracker
        progress = DownloadProgress(
            total_tiles=len(tiles),
            downloaded_tiles=0,
            failed_tiles=0
        )
        
        try:
            # Download tiles concurrently
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all downloads
                future_to_tile = {
                    executor.submit(self._download_tile, tile): tile
                    for tile in tiles
                }
                
                # Process completed downloads
                for future in as_completed(future_to_tile):
                    if self._cancelled:
                        self.logger.info("Download cancelled by user")
                        break
                    
                    result = future.result()
                    
                    if result.success:
                        downloaded_count += 1
                        self._total_bytes += result.file_size
                        self.tile_downloaded.emit(result.tile)
                    else:
                        failed_count += 1
                        self.tile_failed.emit(result.tile, result.error_message or "Unknown error")
                    
                    # Update progress
                    progress.downloaded_tiles = downloaded_count
                    progress.failed_tiles = failed_count
                    progress.current_tile = result.tile
                    
                    # Calculate speed
                    elapsed = time.time() - self._start_time
                    if elapsed > 0:
                        progress.speed_mbps = (self._total_bytes / (1024 * 1024)) / elapsed
                        
                        # Estimate remaining time
                        remaining_tiles = len(tiles) - downloaded_count - failed_count
                        if downloaded_count > 0:
                            avg_time_per_tile = elapsed / downloaded_count
                            progress.estimated_time_remaining = remaining_tiles * avg_time_per_tile
                    
                    self.progress_updated.emit(progress)
            
            # Download complete
            elapsed = time.time() - self._start_time
            self.logger.info(
                f"Download completed: {downloaded_count} succeeded, {failed_count} failed "
                f"in {elapsed:.2f}s"
            )
            
            self.download_completed.emit(downloaded_count, failed_count)
            
        except Exception as e:
            error_msg = f"Download error: {str(e)}"
            self.logger.error(error_msg)
            self.download_error.emit(error_msg)
        
        finally:
            # Clean up session
            if self._session:
                self._session.close()
                self._session = None
    
    def cancel(self):
        """Cancel ongoing download."""
        self.logger.info("Cancelling download")
        self._cancelled = True
    
    def clear_cache(self):
        """Clear tile cache."""
        try:
            import shutil
            if self.cache_dir.exists():
                shutil.rmtree(self.cache_dir)
                self.cache_dir.mkdir(parents=True, exist_ok=True)
                self.logger.info("Cache cleared")
        except Exception as e:
            self.logger.error(f"Failed to clear cache: {str(e)}")
    
    def get_cache_size(self) -> int:
        """
        Get total cache size in bytes.
        
        Returns:
            Cache size in bytes
        """
        total_size = 0
        
        try:
            for file_path in self.cache_dir.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        except Exception as e:
            self.logger.error(f"Failed to calculate cache size: {str(e)}")
        
        return total_size
