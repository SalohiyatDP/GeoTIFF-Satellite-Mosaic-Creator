"""
Raster processing service.
Handles polygon clipping and raster operations.
"""
import logging
from pathlib import Path
from typing import Optional, List

try:
    import rasterio
    from rasterio.mask import mask
    from rasterio.warp import reproject, calculate_default_transform, Resampling
    from rasterio.features import geometry_mask
    import rasterio.shutil
    RASTERIO_AVAILABLE = True
except ImportError:
    RASTERIO_AVAILABLE = False

try:
    from osgeo import gdal
    GDAL_AVAILABLE = True
except ImportError:
    GDAL_AVAILABLE = False

from PyQt6.QtCore import QObject, pyqtSignal

from app.core.models import Polygon
from app.services.polygon_engine import PolygonEngine


class RasterProcessor(QObject):
    """
    Processes raster data with polygon clipping and transformations.
    
    Signals:
        progress_updated: Emitted with progress percentage
        processing_completed: Emitted when processing completes
        processing_error: Emitted on error
    """
    
    progress_updated = pyqtSignal(int)
    processing_completed = pyqtSignal(str)
    processing_error = pyqtSignal(str)
    
    def __init__(self):
        """Initialize raster processor."""
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.polygon_engine = PolygonEngine()
    
    def clip_to_polygon(self, input_path: Path, output_path: Path,
                       polygon: Polygon, crop: bool = True) -> bool:
        """
        Clip raster to polygon boundary.
        
        Args:
            input_path: Path to input raster
            output_path: Path for output clipped raster
            polygon: Polygon for clipping
            crop: If True, crop to polygon extent
            
        Returns:
            True if successful
        """
        if not RASTERIO_AVAILABLE:
            error_msg = "Rasterio not available"
            self.logger.error(error_msg)
            self.processing_error.emit(error_msg)
            return False
        
        try:
            self.logger.info(f"Clipping raster to polygon: {input_path}")
            self.progress_updated.emit(0)
            
            # Convert polygon to Shapely geometry
            shapely_poly = self.polygon_engine.to_shapely(polygon)
            if shapely_poly is None:
                error_msg = "Failed to convert polygon to Shapely geometry"
                self.logger.error(error_msg)
                self.processing_error.emit(error_msg)
                return False
            
            # Convert to GeoJSON-like format
            geom = {
                "type": "Polygon",
                "coordinates": [list(shapely_poly.exterior.coords)]
            }
            
            self.progress_updated.emit(20)
            
            # Open source raster
            with rasterio.open(input_path) as src:
                # Clip raster
                self.logger.info("Performing clip operation...")
                out_image, out_transform = mask(
                    src,
                    [geom],
                    crop=crop,
                    all_touched=True,
                    nodata=0
                )
                
                self.progress_updated.emit(60)
                
                # Update metadata
                out_meta = src.meta.copy()
                out_meta.update({
                    "driver": "GTiff",
                    "height": out_image.shape[1],
                    "width": out_image.shape[2],
                    "transform": out_transform,
                    "compress": "lzw",
                    "nodata": 0
                })
                
                # Write clipped raster
                self.logger.info(f"Writing clipped raster to {output_path}")
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                with rasterio.open(output_path, "w", **out_meta) as dest:
                    dest.write(out_image)
                
                self.progress_updated.emit(100)
            
            self.logger.info(f"Clipping completed: {output_path}")
            self.processing_completed.emit(str(output_path))
            
            return True
            
        except Exception as e:
            error_msg = f"Failed to clip raster: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self.processing_error.emit(error_msg)
            return False
    
    def reproject_raster(self, input_path: Path, output_path: Path,
                        target_crs: str) -> bool:
        """
        Reproject raster to different CRS.
        
        Args:
            input_path: Path to input raster
            output_path: Path for output raster
            target_crs: Target coordinate reference system
            
        Returns:
            True if successful
        """
        if not RASTERIO_AVAILABLE:
            error_msg = "Rasterio not available"
            self.logger.error(error_msg)
            self.processing_error.emit(error_msg)
            return False
        
        try:
            self.logger.info(f"Reprojecting raster to {target_crs}")
            self.progress_updated.emit(0)
            
            with rasterio.open(input_path) as src:
                # Calculate transform and dimensions
                transform, width, height = calculate_default_transform(
                    src.crs,
                    target_crs,
                    src.width,
                    src.height,
                    *src.bounds
                )
                
                self.progress_updated.emit(30)
                
                # Update metadata
                kwargs = src.meta.copy()
                kwargs.update({
                    'crs': target_crs,
                    'transform': transform,
                    'width': width,
                    'height': height,
                    'compress': 'lzw'
                })
                
                # Reproject and write
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                with rasterio.open(output_path, 'w', **kwargs) as dst:
                    for i in range(1, src.count + 1):
                        reproject(
                            source=rasterio.band(src, i),
                            destination=rasterio.band(dst, i),
                            src_transform=src.transform,
                            src_crs=src.crs,
                            dst_transform=transform,
                            dst_crs=target_crs,
                            resampling=Resampling.bilinear
                        )
                
                self.progress_updated.emit(100)
            
            self.logger.info(f"Reprojection completed: {output_path}")
            self.processing_completed.emit(str(output_path))
            
            return True
            
        except Exception as e:
            error_msg = f"Failed to reproject raster: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self.processing_error.emit(error_msg)
            return False
    
    def build_overviews(self, raster_path: Path, 
                       levels: Optional[List[int]] = None) -> bool:
        """
        Build internal overviews (pyramids) for raster.
        
        Args:
            raster_path: Path to raster file
            levels: Overview levels (default: [2, 4, 8, 16])
            
        Returns:
            True if successful
        """
        if not RASTERIO_AVAILABLE:
            return False
        
        if levels is None:
            levels = [2, 4, 8, 16]
        
        try:
            self.logger.info(f"Building overviews for {raster_path}")
            
            with rasterio.open(raster_path, 'r+') as src:
                src.build_overviews(levels, Resampling.average)
                src.update_tags(ns='rio_overview', resampling='average')
            
            self.logger.info("Overviews built successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to build overviews: {str(e)}")
            return False
    
    def get_raster_info(self, raster_path: Path) -> Optional[dict]:
        """
        Get raster metadata and information.
        
        Args:
            raster_path: Path to raster file
            
        Returns:
            Dictionary with raster information or None
        """
        if not RASTERIO_AVAILABLE:
            return None
        
        try:
            with rasterio.open(raster_path) as src:
                info = {
                    'width': src.width,
                    'height': src.height,
                    'count': src.count,
                    'dtype': str(src.dtypes[0]),
                    'crs': str(src.crs) if src.crs else None,
                    'bounds': src.bounds,
                    'transform': src.transform,
                    'nodata': src.nodata,
                    'driver': src.driver,
                    'compression': src.compression
                }
                
                return info
                
        except Exception as e:
            self.logger.error(f"Failed to get raster info: {str(e)}")
            return None
