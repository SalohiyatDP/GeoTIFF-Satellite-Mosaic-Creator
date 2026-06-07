"""
Coordinate management service.
Handles coordinate input, parsing, and transformation.
"""
import csv
import json
from pathlib import Path
from typing import List, Optional, Tuple
import logging

try:
    import geopandas as gpd
    import fiona
    GEOPANDAS_AVAILABLE = True
except ImportError:
    GEOPANDAS_AVAILABLE = False

try:
    from pyproj import Transformer, CRS
    PYPROJ_AVAILABLE = True
except ImportError:
    PYPROJ_AVAILABLE = False

from app.core.models import Coordinate, Polygon
from app.utils.validators import validate_coordinate, validate_epsg_code


class CoordinateManager:
    """Manages coordinate input and transformation."""
    
    def __init__(self):
        """Initialize coordinate manager."""
        self.logger = logging.getLogger(__name__)
    
    def parse_manual_input(self, text: str, crs: str = "EPSG:4326") -> Tuple[List[Coordinate], List[str]]:
        """
        Parse manually entered coordinates from text.
        
        Supports formats:
        - x,y or lon,lat
        - x y or lon lat
        - One coordinate per line
        
        Args:
            text: Text containing coordinates
            crs: Coordinate reference system
            
        Returns:
            Tuple of (coordinates list, error messages)
        """
        coordinates = []
        errors = []
        
        lines = text.strip().split('\n')
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Try comma separator first
            if ',' in line:
                parts = line.split(',')
            else:
                # Try space/tab separator
                parts = line.split()
            
            if len(parts) < 2:
                errors.append(f"Line {i}: Invalid format. Expected 'x,y' or 'x y'")
                continue
            
            try:
                x = float(parts[0].strip())
                y = float(parts[1].strip())
                
                # Validate if WGS84
                if crs == "EPSG:4326":
                    is_valid, error = validate_coordinate(y, x)
                    if not is_valid:
                        errors.append(f"Line {i}: {error}")
                        continue
                
                coordinates.append(Coordinate(x=x, y=y, crs=crs))
                
            except ValueError as e:
                errors.append(f"Line {i}: Invalid number format - {str(e)}")
        
        self.logger.info(f"Parsed {len(coordinates)} coordinates from manual input")
        if errors:
            self.logger.warning(f"Parse errors: {len(errors)}")
        
        return coordinates, errors
    
    def load_from_txt(self, file_path: Path, crs: str = "EPSG:4326") -> Tuple[List[Coordinate], List[str]]:
        """
        Load coordinates from TXT file.
        
        Args:
            file_path: Path to TXT file
            crs: Coordinate reference system
            
        Returns:
            Tuple of (coordinates list, error messages)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            self.logger.info(f"Loading coordinates from TXT: {file_path}")
            return self.parse_manual_input(text, crs)
            
        except Exception as e:
            error_msg = f"Failed to read TXT file: {str(e)}"
            self.logger.error(error_msg)
            return [], [error_msg]
    
    def load_from_csv(self, file_path: Path, x_column: str = "x", 
                     y_column: str = "y", crs: str = "EPSG:4326",
                     delimiter: str = ",") -> Tuple[List[Coordinate], List[str]]:
        """
        Load coordinates from CSV file.
        
        Args:
            file_path: Path to CSV file
            x_column: Name of X/longitude column
            y_column: Name of Y/latitude column
            crs: Coordinate reference system
            delimiter: CSV delimiter
            
        Returns:
            Tuple of (coordinates list, error messages)
        """
        coordinates = []
        errors = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=delimiter)
                
                # Check if columns exist
                if x_column not in reader.fieldnames:
                    return [], [f"Column '{x_column}' not found in CSV"]
                if y_column not in reader.fieldnames:
                    return [], [f"Column '{y_column}' not found in CSV"]
                
                for i, row in enumerate(reader, 2):  # Start from 2 (header is 1)
                    try:
                        x = float(row[x_column])
                        y = float(row[y_column])
                        
                        # Validate if WGS84
                        if crs == "EPSG:4326":
                            is_valid, error = validate_coordinate(y, x)
                            if not is_valid:
                                errors.append(f"Row {i}: {error}")
                                continue
                        
                        coordinates.append(Coordinate(x=x, y=y, crs=crs))
                        
                    except (ValueError, KeyError) as e:
                        errors.append(f"Row {i}: Invalid data - {str(e)}")
            
            self.logger.info(f"Loaded {len(coordinates)} coordinates from CSV: {file_path}")
            if errors:
                self.logger.warning(f"CSV load errors: {len(errors)}")
            
        except Exception as e:
            error_msg = f"Failed to read CSV file: {str(e)}"
            self.logger.error(error_msg)
            return [], [error_msg]
        
        return coordinates, errors
    
    def load_from_shapefile(self, file_path: Path) -> Tuple[Optional[Polygon], List[str]]:
        """
        Load polygon from Shapefile.
        
        Args:
            file_path: Path to Shapefile
            
        Returns:
            Tuple of (Polygon or None, error messages)
        """
        if not GEOPANDAS_AVAILABLE:
            return None, ["GeoPandas not available. Install with: pip install geopandas"]
        
        errors = []
        
        try:
            # Read shapefile
            gdf = gpd.read_file(file_path)
            
            if len(gdf) == 0:
                return None, ["Shapefile is empty"]
            
            # Get first geometry
            geom = gdf.geometry.iloc[0]
            
            # Get CRS
            crs = gdf.crs.to_string() if gdf.crs else "EPSG:4326"
            
            # Extract coordinates
            if geom.geom_type == 'Polygon':
                coords = list(geom.exterior.coords)
            elif geom.geom_type == 'MultiPolygon':
                # Take first polygon
                coords = list(geom.geoms[0].exterior.coords)
            else:
                return None, [f"Unsupported geometry type: {geom.geom_type}"]
            
            # Convert to Coordinate objects
            coordinates = [Coordinate(x=x, y=y, crs=crs) for x, y in coords]
            
            polygon = Polygon(
                coordinates=coordinates,
                crs=crs,
                name=file_path.stem
            )
            
            self.logger.info(f"Loaded polygon from Shapefile: {file_path}")
            self.logger.info(f"Polygon CRS: {crs}, vertices: {len(coordinates)}")
            
            return polygon, errors
            
        except Exception as e:
            error_msg = f"Failed to read Shapefile: {str(e)}"
            self.logger.error(error_msg)
            return None, [error_msg]
    
    def load_from_geojson(self, file_path: Path) -> Tuple[Optional[Polygon], List[str]]:
        """
        Load polygon from GeoJSON file.
        
        Args:
            file_path: Path to GeoJSON file
            
        Returns:
            Tuple of (Polygon or None, error messages)
        """
        errors = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Determine structure
            if data.get('type') == 'FeatureCollection':
                if not data.get('features'):
                    return None, ["GeoJSON FeatureCollection is empty"]
                feature = data['features'][0]
                geom = feature['geometry']
            elif data.get('type') == 'Feature':
                geom = data['geometry']
            elif data.get('type') in ['Polygon', 'MultiPolygon']:
                geom = data
            else:
                return None, [f"Unsupported GeoJSON type: {data.get('type')}"]
            
            # Extract coordinates
            if geom['type'] == 'Polygon':
                coords = geom['coordinates'][0]  # Exterior ring
            elif geom['type'] == 'MultiPolygon':
                coords = geom['coordinates'][0][0]  # First polygon exterior ring
            else:
                return None, [f"Unsupported geometry type: {geom['type']}"]
            
            # Convert to Coordinate objects
            # GeoJSON uses [lon, lat] order
            coordinates = [Coordinate(x=x, y=y, crs="EPSG:4326") for x, y in coords]
            
            polygon = Polygon(
                coordinates=coordinates,
                crs="EPSG:4326",
                name=file_path.stem
            )
            
            self.logger.info(f"Loaded polygon from GeoJSON: {file_path}")
            self.logger.info(f"Vertices: {len(coordinates)}")
            
            return polygon, errors
            
        except Exception as e:
            error_msg = f"Failed to read GeoJSON: {str(e)}"
            self.logger.error(error_msg)
            return None, [error_msg]
    
    def transform_coordinates(self, coordinates: List[Coordinate], 
                            target_crs: str) -> Tuple[List[Coordinate], List[str]]:
        """
        Transform coordinates to different CRS.
        
        Args:
            coordinates: List of coordinates
            target_crs: Target coordinate reference system
            
        Returns:
            Tuple of (transformed coordinates, error messages)
        """
        if not PYPROJ_AVAILABLE:
            return [], ["PyProj not available. Install with: pip install pyproj"]
        
        if not coordinates:
            return [], ["No coordinates to transform"]
        
        errors = []
        transformed = []
        
        try:
            # Get source CRS from first coordinate
            source_crs = coordinates[0].crs
            
            # Validate CRS codes
            is_valid, error = validate_epsg_code(source_crs)
            if not is_valid:
                return [], [error]
            
            is_valid, error = validate_epsg_code(target_crs)
            if not is_valid:
                return [], [error]
            
            # Skip if same CRS
            if source_crs == target_crs:
                return coordinates, []
            
            # Create transformer
            transformer = Transformer.from_crs(source_crs, target_crs, always_xy=True)
            
            # Transform each coordinate
            for coord in coordinates:
                try:
                    x, y = transformer.transform(coord.x, coord.y)
                    transformed.append(Coordinate(x=x, y=y, crs=target_crs))
                except Exception as e:
                    errors.append(f"Failed to transform ({coord.x}, {coord.y}): {str(e)}")
            
            self.logger.info(f"Transformed {len(transformed)} coordinates from {source_crs} to {target_crs}")
            if errors:
                self.logger.warning(f"Transform errors: {len(errors)}")
            
        except Exception as e:
            error_msg = f"Coordinate transformation failed: {str(e)}"
            self.logger.error(error_msg)
            return [], [error_msg]
        
        return transformed, errors
    
    def create_polygon_from_coordinates(self, coordinates: List[Coordinate], 
                                       name: Optional[str] = None) -> Polygon:
        """
        Create a Polygon object from coordinates.
        
        Args:
            coordinates: List of coordinates
            name: Optional polygon name
            
        Returns:
            Polygon object
        """
        if not coordinates:
            return Polygon(coordinates=[], name=name)
        
        crs = coordinates[0].crs
        
        polygon = Polygon(
            coordinates=coordinates,
            crs=crs,
            name=name or "Untitled Polygon"
        )
        
        self.logger.info(f"Created polygon with {len(coordinates)} vertices")
        
        return polygon
    
    def get_csv_columns(self, file_path: Path, delimiter: str = ",") -> Tuple[List[str], Optional[str]]:
        """
        Get column names from CSV file.
        
        Args:
            file_path: Path to CSV file
            delimiter: CSV delimiter
            
        Returns:
            Tuple of (column names, error message)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter=delimiter)
                headers = next(reader)
                return headers, None
        except Exception as e:
            return [], str(e)
