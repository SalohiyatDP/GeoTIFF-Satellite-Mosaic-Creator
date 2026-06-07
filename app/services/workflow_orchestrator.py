"""
Workflow orchestrator service.
Coordinates the complete mosaic generation workflow.
"""
import logging
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal, QThread

from app.core.models import Project, ProcessingStatus, TileInfo
from app.core.config import ConfigManager
from app.services.polygon_engine import PolygonEngine
from app.services.tile_calculator import TileCalculator
from app.services.imagery_provider import ImageryProviderFactory
from app.services.tile_downloader import TileDownloader
from app.services.mosaic_builder import MosaicBuilder
from app.services.raster_processor import RasterProcessor
from app.services.geotiff_exporter import GeoTIFFExporter


class WorkflowOrchestrator(QObject):
    """Orchestrates the complete mosaic generation workflow."""
    
    # Signals
    workflow_started = pyqtSignal()
    status_updated = pyqtSignal(str, str)  # status, message
    progress_updated = pyqtSignal(int)  # percentage
    workflow_completed = pyqtSignal(str)  # output path
    workflow_failed = pyqtSignal(str)  # error message
    
    def __init__(self, config_manager: ConfigManager):
        """
        Initialize workflow orchestrator.
        
        Args:
            config_manager: Configuration manager
        """
        super().__init__()
        
        self.logger = logging.getLogger(__name__)
        self.config_manager = config_manager
        
        # Services
        self.polygon_engine = PolygonEngine()
        self.tile_calculator = TileCalculator()
        
        # State
        self.current_project = None
        self.is_running = False
        self.should_cancel = False
    
    def execute_workflow(self, project: Project):
        """
        Execute complete mosaic generation workflow.
        
        Args:
            project: Project to process
        """
        self.current_project = project
        self.is_running = True
        self.should_cancel = False
        
        self.logger.info(f"Starting workflow for project: {project.name}")
        self.workflow_started.emit()
        
        try:
            # Step 1: Validate polygon
            self._update_status(ProcessingStatus.VALIDATING, "Validating polygon...")
            if not self._validate_polygon():
                return
            
            self.progress_updated.emit(10)
            
            # Step 2: Calculate tiles
            self._update_status(ProcessingStatus.CALCULATING, "Calculating required tiles...")
            if not self._calculate_tiles():
                return
            
            self.progress_updated.emit(20)
            
            # Step 3: Download tiles
            self._update_status(ProcessingStatus.DOWNLOADING, "Downloading tiles...")
            if not self._download_tiles():
                return
            
            self.progress_updated.emit(60)
            
            # Step 4: Build mosaic
            self._update_status(ProcessingStatus.MOSAICKING, "Building mosaic...")
            mosaic_path = self._build_mosaic()
            if not mosaic_path:
                return
            
            self.progress_updated.emit(75)
            
            # Step 5: Clip to polygon (if requested)
            if project.export_settings.clip_to_polygon:
                self._update_status(ProcessingStatus.CLIPPING, "Clipping to polygon...")
                clipped_path = self._clip_mosaic(mosaic_path)
                if not clipped_path:
                    return
                mosaic_path = clipped_path
            
            self.progress_updated.emit(85)
            
            # Step 6: Export to final format
            self._update_status(ProcessingStatus.EXPORTING, "Exporting GeoTIFF...")
            if not self._export_geotiff(mosaic_path):
                return
            
            self.progress_updated.emit(100)
            
            # Success
            project.status = ProcessingStatus.COMPLETED
            self._update_status(ProcessingStatus.COMPLETED, "Workflow completed successfully!")
            
            self.logger.info(f"Workflow completed: {project.output_path}")
            self.workflow_completed.emit(str(project.output_path))
            
        except Exception as e:
            self._handle_error(f"Workflow error: {str(e)}")
        
        finally:
            self.is_running = False
    
    def cancel_workflow(self):
        """Cancel ongoing workflow."""
        self.logger.info("Cancelling workflow")
        self.should_cancel = True
        self.current_project.status = ProcessingStatus.CANCELLED
    
    def _validate_polygon(self) -> bool:
        """Validate polygon geometry."""
        polygon = self.current_project.polygon
        
        is_valid, errors = self.polygon_engine.validate_polygon(polygon)
        
        if not is_valid:
            error_msg = "Polygon validation failed:\n" + "\n".join(errors)
            self._handle_error(error_msg)
            return False
        
        # Calculate bounding box
        bbox = self.polygon_engine.calculate_bounding_box(polygon)
        self.current_project.bounding_box = bbox
        
        self.logger.info("Polygon validation passed")
        return True
    
    def _calculate_tiles(self) -> bool:
        """Calculate required tiles."""
        project = self.current_project
        
        # Get tiles for polygon
        tiles_coords = self.tile_calculator.get_tiles_for_polygon(
            project.polygon,
            project.zoom_level
        )
        
        if not tiles_coords:
            self._handle_error("Failed to calculate tiles")
            return False
        
        # Get provider
        provider_config = self.config_manager.get_provider(project.imagery_provider)
        if not provider_config:
            self._handle_error(f"Provider not found: {project.imagery_provider}")
            return False
        
        provider = ImageryProviderFactory.create(provider_config)
        if not provider:
            self._handle_error("Failed to create provider")
            return False
        
        # Create TileInfo objects
        project.tiles = [
            TileInfo(x=x, y=y, z=z, url=provider.get_tile_url(x, y, z))
            for x, y, z in tiles_coords
        ]
        
        self.logger.info(f"Calculated {len(project.tiles)} tiles")
        return True
    
    def _download_tiles(self) -> bool:
        """Download tiles."""
        project = self.current_project
        
        # Get provider
        provider_config = self.config_manager.get_provider(project.imagery_provider)
        provider = ImageryProviderFactory.create(provider_config)
        
        # Create cache directory
        cache_dir = Path(self.config_manager.config.cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Create downloader
        downloader = TileDownloader(
            provider=provider,
            cache_dir=cache_dir,
            max_workers=self.config_manager.config.max_concurrent_downloads
        )
        
        # Connect signals
        downloader.progress_updated.connect(
            lambda progress: self.progress_updated.emit(
                20 + int(progress.percentage * 0.4)  # Map to 20-60%
            )
        )
        
        # Download tiles
        downloader.download_tiles(project.tiles)
        
        # Check for cancellation
        if self.should_cancel:
            downloader.cancel()
            return False
        
        return True
    
    def _build_mosaic(self) -> Optional[Path]:
        """Build mosaic from tiles."""
        project = self.current_project
        
        # Create temp directory
        temp_dir = Path(self.config_manager.config.cache_dir) / "mosaics"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        mosaic_path = temp_dir / f"{project.name}_mosaic.tif"
        
        # Build mosaic
        builder = MosaicBuilder()
        success = builder.build_mosaic(
            project.tiles,
            mosaic_path,
            target_crs=project.polygon.crs
        )
        
        if not success:
            self._handle_error("Failed to build mosaic")
            return None
        
        return mosaic_path
    
    def _clip_mosaic(self, mosaic_path: Path) -> Optional[Path]:
        """Clip mosaic to polygon."""
        project = self.current_project
        
        clipped_path = mosaic_path.parent / f"{project.name}_clipped.tif"
        
        processor = RasterProcessor()
        success = processor.clip_to_polygon(
            mosaic_path,
            clipped_path,
            project.polygon,
            crop=True
        )
        
        if not success:
            self._handle_error("Failed to clip mosaic")
            return None
        
        return clipped_path
    
    def _export_geotiff(self, input_path: Path) -> bool:
        """Export to final GeoTIFF."""
        project = self.current_project
        
        if not project.output_path:
            self._handle_error("Output path not specified")
            return False
        
        exporter = GeoTIFFExporter()
        success = exporter.export(
            input_path,
            project.output_path,
            project.export_settings
        )
        
        if not success:
            self._handle_error("Failed to export GeoTIFF")
            return False
        
        return True
    
    def _update_status(self, status: ProcessingStatus, message: str):
        """Update workflow status."""
        self.current_project.status = status
        self.status_updated.emit(status.value, message)
        self.logger.info(f"Status: {status.value} - {message}")
    
    def _handle_error(self, error_msg: str):
        """Handle workflow error."""
        self.logger.error(error_msg)
        self.current_project.status = ProcessingStatus.FAILED
        self.current_project.error_message = error_msg
        self.workflow_failed.emit(error_msg)
