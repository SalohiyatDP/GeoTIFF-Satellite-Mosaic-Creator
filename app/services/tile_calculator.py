"""
Tile calculation engine.
Calculates required map tiles for polygon coverage.
"""
import math
import logging
from typing import List, Tuple, Optional

try:
    import mercantile
    from mercantile import Tile, LngLat, Bbox
    MERCANTILE_AVAILABLE = True
except ImportError:
    MERCANTILE_AVAILABLE = False

try:
    from shapely.geometry import Polygon as ShapelyPolygon, box
    SHAPELY_AVAILABLE = True
except ImportError:
    SHAPELY_AVAILABLE = False

from app.core.models import Polygon, BoundingBox, TileInfo, Coordinate


class TileCalculator:
    """Calculates map tiles for polygon coverage."""
    
    def __init__(self):
        """Initialize tile calculator."""
        self.logger = logging.getLogger(__name__)
    
    def calculate_optimal_zoom(self, bbox: BoundingBox, 
                              min_zoom: int = 10, 
                              max_zoom: int = 19,
                              target_tiles: int = 100) -> int:
        """
        Calculate optimal zoom level for polygon.
        
        Tries to find zoom level that provides good quality
        without downloading too many tiles.
        
        Args:
            bbox: Bounding box
            min_zoom: Minimum zoom level
            max_zoom: Maximum zoom level
            target_tiles: Target number of tiles (approximate)
            
        Returns:
            Optimal zoom level
        """
        if not MERCANTILE_AVAILABLE:
            self.logger.warning("Mercantile not available, using default zoom")
            return 15
        
        try:
            # Calculate area in degrees
            width = bbox.width()
            height = bbox.height()
            area = width * height
            
            # Start from max zoom and work down
            for zoom in range(max_zoom, min_zoom - 1, -1):
                tiles = self.get_tiles_for_bbox(bbox, zoom)
                tile_count = len(tiles)
                
                if tile_count <= target_tiles:
                    self.logger.info(f"Optimal zoom level: {zoom} ({tile_count} tiles)")
                    return zoom
            
            # If still too many tiles at min_zoom, return min_zoom
            self.logger.warning(f"Using minimum zoom level: {min_zoom}")
            return min_zoom
            
        except Exception as e:
            self.logger.error(f"Failed to calculate optimal zoom: {str(e)}")
            return 15
    
    def get_tiles_for_bbox(self, bbox: BoundingBox, zoom: int) -> List[Tuple[int, int, int]]:
        """
        Get all tiles that cover a bounding box.
        
        Args:
            bbox: Bounding box
            zoom: Zoom level
            
        Returns:
            List of (x, y, z) tile coordinates
        """
        if not MERCANTILE_AVAILABLE:
            self.logger.error("Mercantile not available")
            return []
        
        try:
            # Get tiles using mercantile
            tiles = list(mercantile.tiles(
                bbox.min_x, bbox.min_y, bbox.max_x, bbox.max_y, 
                zooms=[zoom]
            ))
            
            tile_coords = [(t.x, t.y, t.z) for t in tiles]
            
            self.logger.info(f"Calculated {len(tile_coords)} tiles for zoom {zoom}")
            
            return tile_coords
            
        except Exception as e:
            self.logger.error(f"Failed to get tiles for bbox: {str(e)}")
            return []
    
    def get_tiles_for_polygon(self, polygon: Polygon, zoom: int) -> List[Tuple[int, int, int]]:
        """
        Get tiles that intersect with polygon.
        More precise than bounding box method.
        
        Args:
            polygon: Polygon
            zoom: Zoom level
            
        Returns:
            List of (x, y, z) tile coordinates
        """
        if not MERCANTILE_AVAILABLE or not SHAPELY_AVAILABLE:
            self.logger.error("Mercantile or Shapely not available")
            return []
        
        try:
            # Convert polygon to Shapely
            coords = [(c.x, c.y) for c in polygon.coordinates]
            shapely_poly = ShapelyPolygon(coords)
            
            # Get bounding box tiles first
            xs = [c.x for c in polygon.coordinates]
            ys = [c.y for c in polygon.coordinates]
            
            bbox_tiles = list(mercantile.tiles(
                min(xs), min(ys), max(xs), max(ys),
                zooms=[zoom]
            ))
            
            # Filter tiles that intersect polygon
            intersecting_tiles = []
            
            for tile in bbox_tiles:
                # Get tile bounds
                tile_bbox = mercantile.bounds(tile)
                tile_polygon = box(
                    tile_bbox.west, tile_bbox.south,
                    tile_bbox.east, tile_bbox.north
                )
                
                # Check intersection
                if shapely_poly.intersects(tile_polygon):
                    intersecting_tiles.append((tile.x, tile.y, tile.z))
            
            self.logger.info(
                f"Filtered {len(intersecting_tiles)} tiles from {len(bbox_tiles)} "
                f"bbox tiles (zoom {zoom})"
            )
            
            return intersecting_tiles
            
        except Exception as e:
            self.logger.error(f"Failed to get tiles for polygon: {str(e)}")
            return []
    
    def tile_to_bbox(self, x: int, y: int, z: int) -> Optional[BoundingBox]:
        """
        Get bounding box for a tile.
        
        Args:
            x: Tile X coordinate
            y: Tile Y coordinate
            z: Tile Z (zoom) coordinate
            
        Returns:
            BoundingBox or None if error
        """
        if not MERCANTILE_AVAILABLE:
            return None
        
        try:
            bounds = mercantile.bounds(Tile(x, y, z))
            
            return BoundingBox(
                min_x=bounds.west,
                min_y=bounds.south,
                max_x=bounds.east,
                max_y=bounds.north,
                crs="EPSG:4326"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get tile bbox: {str(e)}")
            return None
    
    def latlon_to_tile(self, lat: float, lon: float, zoom: int) -> Optional[Tuple[int, int, int]]:
        """
        Convert lat/lon to tile coordinates.
        
        Args:
            lat: Latitude
            lon: Longitude
            zoom: Zoom level
            
        Returns:
            Tuple of (x, y, z) or None if error
        """
        if not MERCANTILE_AVAILABLE:
            return None
        
        try:
            tile = mercantile.tile(lon, lat, zoom)
            return (tile.x, tile.y, tile.z)
            
        except Exception as e:
            self.logger.error(f"Failed to convert latlon to tile: {str(e)}")
            return None
    
    def tile_to_latlon(self, x: int, y: int, z: int) -> Optional[Coordinate]:
        """
        Get upper-left corner coordinate of a tile.
        
        Args:
            x: Tile X coordinate
            y: Tile Y coordinate
            z: Tile Z (zoom) coordinate
            
        Returns:
            Coordinate or None if error
        """
        if not MERCANTILE_AVAILABLE:
            return None
        
        try:
            lng_lat = mercantile.ul(Tile(x, y, z))
            
            return Coordinate(
                x=lng_lat.lng,
                y=lng_lat.lat,
                crs="EPSG:4326"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to convert tile to latlon: {str(e)}")
            return None
    
    def calculate_tile_coverage(self, tiles: List[Tuple[int, int, int]], 
                               tile_size: int = 256) -> Tuple[int, int]:
        """
        Calculate total pixel dimensions of tile coverage.
        
        Args:
            tiles: List of (x, y, z) tile coordinates
            tile_size: Size of each tile in pixels
            
        Returns:
            Tuple of (width, height) in pixels
        """
        if not tiles:
            return (0, 0)
        
        try:
            # Get extent of tiles
            xs = [t[0] for t in tiles]
            ys = [t[1] for t in tiles]
            
            min_x = min(xs)
            max_x = max(xs)
            min_y = min(ys)
            max_y = max(ys)
            
            width = (max_x - min_x + 1) * tile_size
            height = (max_y - min_y + 1) * tile_size
            
            self.logger.info(f"Tile coverage: {width}x{height} pixels")
            
            return (width, height)
            
        except Exception as e:
            self.logger.error(f"Failed to calculate coverage: {str(e)}")
            return (0, 0)
    
    def estimate_download_size(self, num_tiles: int, 
                              avg_tile_size_kb: float = 30.0) -> float:
        """
        Estimate total download size.
        
        Args:
            num_tiles: Number of tiles
            avg_tile_size_kb: Average tile size in KB
            
        Returns:
            Estimated size in MB
        """
        size_mb = (num_tiles * avg_tile_size_kb) / 1024.0
        self.logger.info(f"Estimated download size: {size_mb:.2f} MB for {num_tiles} tiles")
        return size_mb
    
    def get_tile_grid_extent(self, tiles: List[Tuple[int, int, int]]) -> Optional[Tuple[int, int, int, int]]:
        """
        Get extent of tile grid in tile coordinates.
        
        Args:
            tiles: List of (x, y, z) tile coordinates
            
        Returns:
            Tuple of (min_x, min_y, max_x, max_y) or None
        """
        if not tiles:
            return None
        
        try:
            xs = [t[0] for t in tiles]
            ys = [t[1] for t in tiles]
            
            return (min(xs), min(ys), max(xs), max(ys))
            
        except Exception as e:
            self.logger.error(f"Failed to get grid extent: {str(e)}")
            return None
