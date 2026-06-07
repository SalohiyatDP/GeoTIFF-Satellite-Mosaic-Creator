"""
Mosaic builder service.
Merges downloaded tiles into seamless raster mosaic using GDAL/Rasterio.
"""
import logging
from pathlib import Path
from typing import List, Optional, Tuple
import numpy as np

try:
    import rasterio
    from rasterio.merge import merge
    from rasterio.transform import from_bounds
    from rasterio.warp import calculate_default_transform, reproject, Resampling
    from rasterio.enums import ColorInterp
    RASTERIO_AVAILABLE = True
except ImportError:
    RASTERIO_AVAILABLE = False

try:
    from osgeo import gdal, osr
    GDAL_AVAILABLE = True
except ImportError:
    GDAL_AVAILABLE = False

from PyQt6.QtCore import QObject, pyqtSignal

from app.core.models import TileInfo, BoundingBox


class MosaicBuilder(QObject):
    """
    Builds seamless raster mosaics from tiles.
    
    Signals:
        progress_updated: Emitted with progress percentage
        mosaic_completed: Emitted when mosaic is complete
        mosaic_error: Emitted on error
    """
    
    progress_updated = pyqtSignal(int)  # percentage
    mosaic_completed = pyqtSignal(str)  # output path
    mosaic_error = pyqtSignal(str)  # error message
    
    def __init__(self):
        """Initialize mosaic builder."""
        super().__init__()
        self.logger = logging.getLogger(__name__)
    
    def build_mosaic(self, tiles: List[TileInfo], output_path: Path, 
                    target_crs: str = "EPSG:4326") -> bool:
        """
        Build mosaic from tiles using Rasterio.
        
        Args:
            tiles: List of downloaded tiles
            output_path: Path for output mosaic
            target_crs: Target coordinate reference system
            
        Returns:
            True if successful
        """
        if not RASTERIO_AVAILABLE:
            error_msg = "Rasterio not available. Install with: pip install rasterio"
            self.logger.error(error_msg)
            self.mosaic_error.emit(error_msg)
            return False
        
        try:
            self.logger.info(f"Building mosaic from {len(tiles)} tiles")
            self.progress_updated.emit(0)
            
            # Filter successfully downloaded tiles
            downloaded_tiles = [t for t in tiles if t.downloaded and t.file_path]
            
            if not downloaded_tiles:
                error_msg = "No downloaded tiles to mosaic"
                self.logger.error(error_msg)
                self.mosaic_error.emit(error_msg)
                return False
            
            self.logger.info(f"Processing {len(downloaded_tiles)} downloaded tiles")
            
            # Open all tile files
            tile_datasets = []
            for tile in downloaded_tiles:
                try:
                    ds = rasterio.open(tile.file_path)
                    tile_datasets.append(ds)
                except Exception as e:
                    self.logger.warning(f"Failed to open tile {tile.file_path}: {str(e)}")
            
            if not tile_datasets:
                error_msg = "Failed to open any tile datasets"
                self.logger.error(error_msg)
                self.mosaic_error.emit(error_msg)
                return False
            
            self.progress_updated.emit(20)
            
            # Merge tiles
            self.logger.info("Merging tiles...")
            mosaic_array, mosaic_transform = merge(
                tile_datasets,
                resampling=Resampling.bilinear
            )
            
            self.progress_updated.emit(60)
            
            # Get metadata from first tile
            first_tile = tile_datasets[0]
            
            # Prepare output metadata
            out_meta = first_tile.meta.copy()
            out_meta.update({
                "driver": "GTiff",
                "height": mosaic_array.shape[1],
                "width": mosaic_array.shape[2],
                "transform": mosaic_transform,
                "crs": target_crs,
                "compress": "lzw"
            })
            
            # Write mosaic
            self.logger.info(f"Writing mosaic to {output_path}")
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with rasterio.open(output_path, "w", **out_meta) as dest:
                dest.write(mosaic_array)
                
                # Set color interpretation for RGB
                if mosaic_array.shape[0] >= 3:
                    dest.colorinterp = [
                        ColorInterp.red,
                        ColorInterp.green,
                        ColorInterp.blue
                    ]
            
            self.progress_updated.emit(100)
            
            # Close all datasets
            for ds in tile_datasets:
                ds.close()
            
            self.logger.info(f"Mosaic completed: {output_path}")
            self.mosaic_completed.emit(str(output_path))
            
            return True
            
        except Exception as e:
            error_msg = f"Failed to build mosaic: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self.mosaic_error.emit(error_msg)
            return False
    
    def build_mosaic_gdal(self, tiles: List[TileInfo], output_path: Path,
                         bbox: BoundingBox, zoom: int, tile_size: int = 256) -> bool:
        """
        Build mosaic using GDAL VRT (alternative method).
        
        Args:
            tiles: List of downloaded tiles
            output_path: Path for output mosaic
            bbox: Bounding box for mosaic
            zoom: Zoom level
            tile_size: Size of each tile in pixels
            
        Returns:
            True if successful
        """
        if not GDAL_AVAILABLE:
            error_msg = "GDAL not available"
            self.logger.error(error_msg)
            self.mosaic_error.emit(error_msg)
            return False
        
        try:
            self.logger.info(f"Building mosaic with GDAL from {len(tiles)} tiles")
            self.progress_updated.emit(0)
            
            # Filter downloaded tiles
            downloaded_tiles = [t for t in tiles if t.downloaded and t.file_path]
            
            if not downloaded_tiles:
                error_msg = "No downloaded tiles"
                self.logger.error(error_msg)
                self.mosaic_error.emit(error_msg)
                return False
            
            # Get tile grid extent
            xs = [t.x for t in downloaded_tiles]
            ys = [t.y for t in downloaded_tiles]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
            
            # Calculate output dimensions
            width = (max_x - min_x + 1) * tile_size
            height = (max_y - min_y + 1) * tile_size
            
            self.logger.info(f"Output dimensions: {width}x{height}")
            
            # Create VRT
            vrt_path = output_path.with_suffix('.vrt')
            
            vrt_options = gdal.BuildVRTOptions(
                resolution='highest',
                resampleAlg='bilinear'
            )
            
            tile_paths = [str(t.file_path) for t in downloaded_tiles]
            vrt_ds = gdal.BuildVRT(str(vrt_path), tile_paths, options=vrt_options)
            
            if vrt_ds is None:
                error_msg = "Failed to create VRT"
                self.logger.error(error_msg)
                self.mosaic_error.emit(error_msg)
                return False
            
            self.progress_updated.emit(50)
            
            # Translate VRT to GeoTIFF
            translate_options = gdal.TranslateOptions(
                format='GTiff',
                creationOptions=['COMPRESS=LZW', 'TILED=YES']
            )
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            output_ds = gdal.Translate(
                str(output_path),
                vrt_ds,
                options=translate_options
            )
            
            if output_ds is None:
                error_msg = "Failed to translate VRT to GeoTIFF"
                self.logger.error(error_msg)
                self.mosaic_error.emit(error_msg)
                return False
            
            # Close datasets
            output_ds = None
            vrt_ds = None
            
            self.progress_updated.emit(100)
            
            self.logger.info(f"Mosaic completed: {output_path}")
            self.mosaic_completed.emit(str(output_path))
            
            return True
            
        except Exception as e:
            error_msg = f"Failed to build mosaic with GDAL: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self.mosaic_error.emit(error_msg)
            return False
    
    def calculate_mosaic_bounds(self, tiles: List[TileInfo], 
                               tile_size: int = 256) -> Optional[BoundingBox]:
        """
        Calculate geographic bounds of mosaic.
        
        Args:
            tiles: List of tiles
            tile_size: Size of each tile in pixels
            
        Returns:
            BoundingBox or None
        """
        if not tiles:
            return None
        
        try:
            # Get tile extent
            xs = [t.x for t in tiles]
            ys = [t.y for t in tiles]
            z = tiles[0].z
            
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
            
            # Calculate geographic bounds
            # This is approximate - actual calculation requires mercantile
            from app.services.tile_calculator import TileCalculator
            
            calc = TileCalculator()
            
            # Get bounds of corner tiles
            min_tile_bbox = calc.tile_to_bbox(min_x, max_y, z)  # Upper left
            max_tile_bbox = calc.tile_to_bbox(max_x, min_y, z)  # Lower right
            
            if min_tile_bbox and max_tile_bbox:
                return BoundingBox(
                    min_x=min_tile_bbox.min_x,
                    min_y=max_tile_bbox.min_y,
                    max_x=max_tile_bbox.max_x,
                    max_y=min_tile_bbox.max_y,
                    crs="EPSG:4326"
                )
            
        except Exception as e:
            self.logger.error(f"Failed to calculate mosaic bounds: {str(e)}")
        
        return None
