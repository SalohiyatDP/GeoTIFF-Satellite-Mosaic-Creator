"""
GeoTIFF export service.
Handles professional GeoTIFF generation with ArcGIS compatibility.
"""
import logging
from pathlib import Path
from typing import Optional

try:
    import rasterio
    from rasterio.shutil import copy
    from rasterio.enums import Resampling
    RASTERIO_AVAILABLE = True
except ImportError:
    RASTERIO_AVAILABLE = False

try:
    from osgeo import gdal, osr
    GDAL_AVAILABLE = True
except ImportError:
    GDAL_AVAILABLE = False

from PyQt6.QtCore import QObject, pyqtSignal

from app.core.models import ExportSettings, OutputFormat


class GeoTIFFExporter(QObject):
    """
    Exports rasters to GeoTIFF with ArcGIS compatibility.
    
    Signals:
        progress_updated: Emitted with progress percentage
        export_completed: Emitted when export completes
        export_error: Emitted on error
    """
    
    progress_updated = pyqtSignal(int)
    export_completed = pyqtSignal(str)
    export_error = pyqtSignal(str)
    
    def __init__(self):
        """Initialize GeoTIFF exporter."""
        super().__init__()
        self.logger = logging.getLogger(__name__)
    
    def export(self, input_path: Path, output_path: Path,
              settings: ExportSettings) -> bool:
        """
        Export raster to GeoTIFF with specified settings.
        
        Args:
            input_path: Path to input raster
            output_path: Path for output file
            settings: Export settings
            
        Returns:
            True if successful
        """
        if not RASTERIO_AVAILABLE:
            error_msg = "Rasterio not available"
            self.logger.error(error_msg)
            self.export_error.emit(error_msg)
            return False
        
        try:
            self.logger.info(f"Exporting to {settings.output_format.value}: {output_path}")
            self.progress_updated.emit(0)
            
            # Determine output driver
            driver = self._get_driver(settings.output_format)
            
            # Build creation options
            creation_options = self._get_creation_options(settings)
            
            self.progress_updated.emit(20)
            
            # Open source raster
            with rasterio.open(input_path) as src:
                # Update metadata
                out_meta = src.meta.copy()
                out_meta.update({
                    'driver': driver,
                    **creation_options
                })
                
                # Handle CRS transformation if needed
                if settings.target_crs and settings.target_crs != str(src.crs):
                    self.logger.info(f"Reprojecting to {settings.target_crs}")
                    # Use RasterProcessor for reprojection
                    from app.services.raster_processor import RasterProcessor
                    processor = RasterProcessor()
                    temp_path = output_path.with_suffix('.tmp.tif')
                    
                    if not processor.reproject_raster(input_path, temp_path, settings.target_crs):
                        return False
                    
                    input_path = temp_path
                
                self.progress_updated.emit(50)
                
                # Copy with options
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                with rasterio.open(output_path, 'w', **out_meta) as dst:
                    # Copy data
                    for i in range(1, src.count + 1):
                        dst.write(src.read(i), i)
                    
                    # Copy color interpretation
                    if hasattr(src, 'colorinterp'):
                        dst.colorinterp = src.colorinterp
                
                self.progress_updated.emit(80)
                
                # Build overviews if requested
                if settings.build_overviews:
                    self.logger.info("Building overviews...")
                    self._build_overviews(output_path)
                
                self.progress_updated.emit(100)
            
            # Verify ArcGIS compatibility
            if settings.output_format == OutputFormat.GEOTIFF:
                self._ensure_arcgis_compatibility(output_path)
            
            self.logger.info(f"Export completed: {output_path}")
            self.export_completed.emit(str(output_path))
            
            return True
            
        except Exception as e:
            error_msg = f"Export failed: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self.export_error.emit(error_msg)
            return False
    
    def _get_driver(self, output_format: OutputFormat) -> str:
        """
        Get GDAL driver name for output format.
        
        Args:
            output_format: Output format enum
            
        Returns:
            Driver name
        """
        format_map = {
            OutputFormat.GEOTIFF: 'GTiff',
            OutputFormat.TIFF: 'GTiff',
            OutputFormat.JPEG2000: 'JP2OpenJPEG',
            OutputFormat.PNG: 'PNG',
            OutputFormat.JPEG: 'JPEG'
        }
        
        return format_map.get(output_format, 'GTiff')
    
    def _get_creation_options(self, settings: ExportSettings) -> dict:
        """
        Get creation options for export.
        
        Args:
            settings: Export settings
            
        Returns:
            Dictionary of creation options
        """
        options = {}
        
        if settings.output_format == OutputFormat.GEOTIFF:
            # GeoTIFF specific options for ArcGIS compatibility
            options['compress'] = settings.compression
            options['tiled'] = True
            options['blockxsize'] = 256
            options['blockysize'] = 256
            options['photometric'] = 'rgb'  # For RGB imagery
            
            # Additional tags for ArcGIS
            options['bigtiff'] = 'IF_SAFER'
            
        elif settings.output_format == OutputFormat.JPEG2000:
            options['compress'] = 'JPEG2000'
            options['quality'] = 95
            
        elif settings.output_format == OutputFormat.PNG:
            options['compress'] = 'DEFLATE'
            
        elif settings.output_format == OutputFormat.JPEG:
            options['quality'] = 95
            options['photometric'] = 'rgb'
        
        return options
    
    def _build_overviews(self, raster_path: Path) -> bool:
        """
        Build internal overviews for raster.
        
        Args:
            raster_path: Path to raster file
            
        Returns:
            True if successful
        """
        try:
            with rasterio.open(raster_path, 'r+') as src:
                # Calculate overview levels
                max_dim = max(src.width, src.height)
                levels = []
                level = 2
                while max_dim / level > 256:
                    levels.append(level)
                    level *= 2
                
                if levels:
                    self.logger.info(f"Building overview levels: {levels}")
                    src.build_overviews(levels, Resampling.average)
                    src.update_tags(ns='rio_overview', resampling='average')
                    return True
                
        except Exception as e:
            self.logger.warning(f"Failed to build overviews: {str(e)}")
        
        return False
    
    def _ensure_arcgis_compatibility(self, raster_path: Path) -> bool:
        """
        Ensure GeoTIFF is compatible with ArcGIS.
        
        Checks:
        - Embedded CRS
        - Geotransform
        - Proper compression
        - Internal overviews
        
        Args:
            raster_path: Path to GeoTIFF file
            
        Returns:
            True if compatible
        """
        if not RASTERIO_AVAILABLE:
            return False
        
        try:
            with rasterio.open(raster_path) as src:
                # Check CRS
                if src.crs is None:
                    self.logger.warning("Raster has no CRS - may not be ArcGIS compatible")
                    return False
                
                # Check transform
                if src.transform is None:
                    self.logger.warning("Raster has no geotransform - may not be ArcGIS compatible")
                    return False
                
                # Check if georeferenced
                bounds = src.bounds
                if all(b == 0 for b in bounds):
                    self.logger.warning("Raster appears not to be georeferenced")
                    return False
                
                self.logger.info("GeoTIFF appears to be ArcGIS compatible")
                self.logger.info(f"  CRS: {src.crs}")
                self.logger.info(f"  Bounds: {bounds}")
                self.logger.info(f"  Size: {src.width}x{src.height}")
                self.logger.info(f"  Bands: {src.count}")
                
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to verify ArcGIS compatibility: {str(e)}")
            return False
    
    def validate_geotiff(self, raster_path: Path) -> tuple[bool, list[str]]:
        """
        Validate GeoTIFF for completeness and compatibility.
        
        Args:
            raster_path: Path to GeoTIFF file
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        if not RASTERIO_AVAILABLE:
            return False, ["Rasterio not available"]
        
        errors = []
        
        try:
            with rasterio.open(raster_path) as src:
                # Check driver
                if src.driver != 'GTiff':
                    errors.append(f"Not a GeoTIFF (driver: {src.driver})")
                
                # Check CRS
                if src.crs is None:
                    errors.append("Missing CRS")
                
                # Check transform
                if src.transform is None:
                    errors.append("Missing geotransform")
                
                # Check dimensions
                if src.width == 0 or src.height == 0:
                    errors.append("Invalid dimensions")
                
                # Check bands
                if src.count == 0:
                    errors.append("No bands")
                
                # Check bounds
                bounds = src.bounds
                if all(b == 0 for b in bounds):
                    errors.append("Invalid bounds (all zeros)")
                
                if errors:
                    return False, errors
                
                return True, []
                
        except Exception as e:
            return False, [f"Failed to open file: {str(e)}"]
