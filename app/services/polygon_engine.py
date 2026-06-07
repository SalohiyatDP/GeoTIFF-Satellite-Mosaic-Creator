"""
Polygon geometry engine.
Handles polygon validation, geometry operations, and analysis.
"""
import logging
from typing import List, Tuple, Optional

try:
    from shapely.geometry import Polygon as ShapelyPolygon, Point, LineString
    from shapely.validation import make_valid
    from shapely import is_valid, is_simple
    SHAPELY_AVAILABLE = True
except ImportError:
    SHAPELY_AVAILABLE = False

try:
    import geopandas as gpd
    GEOPANDAS_AVAILABLE = True
except ImportError:
    GEOPANDAS_AVAILABLE = False

from app.core.models import Polygon, Coordinate, BoundingBox


class PolygonEngine:
    """Manages polygon geometry operations."""
    
    def __init__(self):
        """Initialize polygon engine."""
        self.logger = logging.getLogger(__name__)
    
    def validate_polygon(self, polygon: Polygon) -> Tuple[bool, List[str]]:
        """
        Validate polygon geometry.
        
        Checks:
        - Minimum 3 vertices
        - Closed polygon
        - No self-intersections
        - Valid geometry
        
        Args:
            polygon: Polygon to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        if not SHAPELY_AVAILABLE:
            return False, ["Shapely not available. Install with: pip install shapely"]
        
        errors = []
        
        # Check minimum vertices
        if len(polygon.coordinates) < 3:
            errors.append("Polygon must have at least 3 vertices")
            return False, errors
        
        try:
            # Convert to Shapely polygon
            coords = [(c.x, c.y) for c in polygon.coordinates]
            
            # Auto-close if not closed
            if coords[0] != coords[-1]:
                coords.append(coords[0])
                self.logger.info("Auto-closing polygon")
            
            shapely_poly = ShapelyPolygon(coords)
            
            # Check if valid
            if not is_valid(shapely_poly):
                errors.append("Invalid polygon geometry")
                
                # Try to get more details
                if not is_simple(shapely_poly):
                    errors.append("Polygon has self-intersections")
                
                if shapely_poly.is_empty:
                    errors.append("Polygon is empty")
            
            # Check area
            if shapely_poly.area == 0:
                errors.append("Polygon has zero area (all points are collinear)")
            
            # Additional checks
            if len(shapely_poly.exterior.coords) != len(set(shapely_poly.exterior.coords)):
                errors.append("Polygon has duplicate consecutive vertices")
            
            if errors:
                self.logger.warning(f"Polygon validation failed: {errors}")
                return False, errors
            
            self.logger.info("Polygon validation passed")
            return True, []
            
        except Exception as e:
            error_msg = f"Polygon validation error: {str(e)}"
            self.logger.error(error_msg)
            return False, [error_msg]
    
    def close_polygon(self, polygon: Polygon) -> Polygon:
        """
        Ensure polygon is closed (first and last vertices are the same).
        
        Args:
            polygon: Input polygon
            
        Returns:
            Closed polygon
        """
        if len(polygon.coordinates) < 2:
            return polygon
        
        first = polygon.coordinates[0]
        last = polygon.coordinates[-1]
        
        # Check if already closed
        if first.x == last.x and first.y == last.y:
            return polygon
        
        # Add closing vertex
        closed_coords = polygon.coordinates + [Coordinate(x=first.x, y=first.y, crs=first.crs)]
        
        return Polygon(
            coordinates=closed_coords,
            crs=polygon.crs,
            name=polygon.name,
            is_valid=polygon.is_valid,
            validation_errors=polygon.validation_errors
        )
    
    def fix_self_intersections(self, polygon: Polygon) -> Tuple[Optional[Polygon], List[str]]:
        """
        Attempt to fix self-intersecting polygon.
        
        Args:
            polygon: Input polygon
            
        Returns:
            Tuple of (fixed polygon or None, error messages)
        """
        if not SHAPELY_AVAILABLE:
            return None, ["Shapely not available"]
        
        errors = []
        
        try:
            coords = [(c.x, c.y) for c in polygon.coordinates]
            shapely_poly = ShapelyPolygon(coords)
            
            if is_valid(shapely_poly):
                return polygon, []
            
            # Try to fix
            fixed_poly = make_valid(shapely_poly)
            
            if fixed_poly.is_empty:
                return None, ["Cannot fix polygon: result is empty"]
            
            # Extract coordinates from largest polygon if MultiPolygon
            if fixed_poly.geom_type == 'MultiPolygon':
                self.logger.warning("Fixed polygon is MultiPolygon, taking largest part")
                fixed_poly = max(fixed_poly.geoms, key=lambda p: p.area)
            
            if fixed_poly.geom_type != 'Polygon':
                return None, [f"Cannot fix polygon: result is {fixed_poly.geom_type}"]
            
            # Convert back to Coordinate objects
            fixed_coords = [
                Coordinate(x=x, y=y, crs=polygon.crs)
                for x, y in fixed_poly.exterior.coords
            ]
            
            fixed_polygon = Polygon(
                coordinates=fixed_coords,
                crs=polygon.crs,
                name=polygon.name
            )
            
            self.logger.info("Successfully fixed polygon self-intersections")
            return fixed_polygon, []
            
        except Exception as e:
            error_msg = f"Failed to fix polygon: {str(e)}"
            self.logger.error(error_msg)
            return None, [error_msg]
    
    def calculate_bounding_box(self, polygon: Polygon) -> Optional[BoundingBox]:
        """
        Calculate polygon bounding box.
        
        Args:
            polygon: Input polygon
            
        Returns:
            BoundingBox or None if error
        """
        if not polygon.coordinates:
            return None
        
        try:
            xs = [c.x for c in polygon.coordinates]
            ys = [c.y for c in polygon.coordinates]
            
            bbox = BoundingBox(
                min_x=min(xs),
                min_y=min(ys),
                max_x=max(xs),
                max_y=max(ys),
                crs=polygon.crs
            )
            
            self.logger.info(f"Calculated bounding box: {bbox.to_tuple()}")
            
            return bbox
            
        except Exception as e:
            self.logger.error(f"Failed to calculate bounding box: {str(e)}")
            return None
    
    def get_polygon_area(self, polygon: Polygon) -> Optional[float]:
        """
        Calculate polygon area in square degrees or square meters.
        
        Args:
            polygon: Input polygon
            
        Returns:
            Area or None if error
        """
        if not SHAPELY_AVAILABLE:
            self.logger.error("Shapely not available")
            return None
        
        try:
            coords = [(c.x, c.y) for c in polygon.coordinates]
            shapely_poly = ShapelyPolygon(coords)
            
            area = shapely_poly.area
            self.logger.info(f"Calculated polygon area: {area}")
            
            return area
            
        except Exception as e:
            self.logger.error(f"Failed to calculate area: {str(e)}")
            return None
    
    def get_polygon_centroid(self, polygon: Polygon) -> Optional[Coordinate]:
        """
        Calculate polygon centroid.
        
        Args:
            polygon: Input polygon
            
        Returns:
            Centroid coordinate or None if error
        """
        if not SHAPELY_AVAILABLE:
            self.logger.error("Shapely not available")
            return None
        
        try:
            coords = [(c.x, c.y) for c in polygon.coordinates]
            shapely_poly = ShapelyPolygon(coords)
            
            centroid = shapely_poly.centroid
            
            result = Coordinate(
                x=centroid.x,
                y=centroid.y,
                crs=polygon.crs
            )
            
            self.logger.info(f"Calculated centroid: ({result.x}, {result.y})")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to calculate centroid: {str(e)}")
            return None
    
    def simplify_polygon(self, polygon: Polygon, tolerance: float = 0.0001) -> Optional[Polygon]:
        """
        Simplify polygon by removing vertices within tolerance.
        
        Args:
            polygon: Input polygon
            tolerance: Simplification tolerance
            
        Returns:
            Simplified polygon or None if error
        """
        if not SHAPELY_AVAILABLE:
            return None
        
        try:
            coords = [(c.x, c.y) for c in polygon.coordinates]
            shapely_poly = ShapelyPolygon(coords)
            
            simplified = shapely_poly.simplify(tolerance, preserve_topology=True)
            
            simplified_coords = [
                Coordinate(x=x, y=y, crs=polygon.crs)
                for x, y in simplified.exterior.coords
            ]
            
            result = Polygon(
                coordinates=simplified_coords,
                crs=polygon.crs,
                name=polygon.name
            )
            
            self.logger.info(f"Simplified polygon: {len(polygon.coordinates)} -> {len(simplified_coords)} vertices")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to simplify polygon: {str(e)}")
            return None
    
    def to_shapely(self, polygon: Polygon) -> Optional[ShapelyPolygon]:
        """
        Convert to Shapely Polygon.
        
        Args:
            polygon: Input polygon
            
        Returns:
            Shapely Polygon or None if error
        """
        if not SHAPELY_AVAILABLE:
            return None
        
        try:
            coords = [(c.x, c.y) for c in polygon.coordinates]
            return ShapelyPolygon(coords)
        except Exception as e:
            self.logger.error(f"Failed to convert to Shapely: {str(e)}")
            return None
    
    def to_geodataframe(self, polygon: Polygon) -> Optional['gpd.GeoDataFrame']:
        """
        Convert to GeoPandas GeoDataFrame.
        
        Args:
            polygon: Input polygon
            
        Returns:
            GeoDataFrame or None if error
        """
        if not GEOPANDAS_AVAILABLE:
            return None
        
        try:
            shapely_poly = self.to_shapely(polygon)
            if shapely_poly is None:
                return None
            
            gdf = gpd.GeoDataFrame(
                {'name': [polygon.name or 'polygon']},
                geometry=[shapely_poly],
                crs=polygon.crs
            )
            
            return gdf
            
        except Exception as e:
            self.logger.error(f"Failed to convert to GeoDataFrame: {str(e)}")
            return None
