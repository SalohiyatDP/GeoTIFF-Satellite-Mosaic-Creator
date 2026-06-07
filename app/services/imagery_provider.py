"""
Imagery provider service.
Handles different imagery sources (XYZ, WMTS, WMS, ArcGIS).
"""
import logging
from typing import Optional, Dict, Any
from urllib.parse import urlparse

from app.core.config import ImageryProviderConfig


class ImageryProvider:
    """Base class for imagery providers."""
    
    def __init__(self, config: ImageryProviderConfig):
        """
        Initialize imagery provider.
        
        Args:
            config: Provider configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def get_tile_url(self, x: int, y: int, z: int) -> str:
        """
        Get URL for a specific tile.
        
        Args:
            x: Tile X coordinate
            y: Tile Y coordinate
            z: Tile Z (zoom) coordinate
            
        Returns:
            Tile URL
        """
        raise NotImplementedError
    
    def get_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers for requests.
        
        Returns:
            Dictionary of headers
        """
        headers = {
            'User-Agent': 'GeoTIFF-Mosaic-Creator/1.0'
        }
        
        if self.config.headers:
            headers.update(self.config.headers)
        
        return headers
    
    def validate_config(self) -> bool:
        """
        Validate provider configuration.
        
        Returns:
            True if valid
        """
        if not self.config.url:
            self.logger.error("Provider URL is empty")
            return False
        
        if self.config.max_zoom < 0:
            self.logger.error("Invalid max_zoom")
            return False
        
        return True


class XYZProvider(ImageryProvider):
    """XYZ tile provider."""
    
    def get_tile_url(self, x: int, y: int, z: int) -> str:
        """
        Get URL for XYZ tile.
        
        XYZ format: https://example.com/{z}/{x}/{y}.png
        
        Args:
            x: Tile X coordinate
            y: Tile Y coordinate
            z: Tile Z (zoom) coordinate
            
        Returns:
            Tile URL
        """
        url = self.config.url
        url = url.replace('{z}', str(z))
        url = url.replace('{x}', str(x))
        url = url.replace('{y}', str(y))
        
        # Support alternative formats
        url = url.replace('{zoom}', str(z))
        
        return url


class WMTSProvider(ImageryProvider):
    """WMTS (Web Map Tile Service) provider."""
    
    def __init__(self, config: ImageryProviderConfig):
        """Initialize WMTS provider."""
        super().__init__(config)
        
        # WMTS specific parameters
        self.layer = config.headers.get('layer', 'default') if config.headers else 'default'
        self.style = config.headers.get('style', 'default') if config.headers else 'default'
        self.tile_matrix_set = config.headers.get('tile_matrix_set', 'GoogleMapsCompatible') if config.headers else 'GoogleMapsCompatible'
        self.format = config.headers.get('format', 'image/png') if config.headers else 'image/png'
    
    def get_tile_url(self, x: int, y: int, z: int) -> str:
        """
        Get URL for WMTS tile.
        
        Args:
            x: Tile X coordinate
            y: Tile Y coordinate
            z: Tile Z (zoom) coordinate
            
        Returns:
            Tile URL
        """
        # Build WMTS URL
        base_url = self.config.url.rstrip('?')
        
        params = [
            f"SERVICE=WMTS",
            f"REQUEST=GetTile",
            f"VERSION=1.0.0",
            f"LAYER={self.layer}",
            f"STYLE={self.style}",
            f"TILEMATRIXSET={self.tile_matrix_set}",
            f"TILEMATRIX={z}",
            f"TILEROW={y}",
            f"TILECOL={x}",
            f"FORMAT={self.format}"
        ]
        
        return f"{base_url}?{'&'.join(params)}"


class WMSProvider(ImageryProvider):
    """WMS (Web Map Service) provider."""
    
    def __init__(self, config: ImageryProviderConfig):
        """Initialize WMS provider."""
        super().__init__(config)
        
        # WMS specific parameters
        self.layers = config.headers.get('layers', '') if config.headers else ''
        self.styles = config.headers.get('styles', '') if config.headers else ''
        self.format = config.headers.get('format', 'image/png') if config.headers else 'image/png'
        self.crs = config.headers.get('crs', 'EPSG:3857') if config.headers else 'EPSG:3857'
        self.tile_size = 256
    
    def get_tile_url(self, x: int, y: int, z: int) -> str:
        """
        Get URL for WMS tile.
        
        Converts tile coordinates to bbox and requests WMS image.
        
        Args:
            x: Tile X coordinate
            y: Tile Y coordinate
            z: Tile Z (zoom) coordinate
            
        Returns:
            Tile URL
        """
        # Calculate bbox from tile coordinates
        bbox = self._tile_to_bbox(x, y, z)
        
        base_url = self.config.url.rstrip('?')
        
        params = [
            f"SERVICE=WMS",
            f"REQUEST=GetMap",
            f"VERSION=1.3.0",
            f"LAYERS={self.layers}",
            f"STYLES={self.styles}",
            f"CRS={self.crs}",
            f"BBOX={bbox}",
            f"WIDTH={self.tile_size}",
            f"HEIGHT={self.tile_size}",
            f"FORMAT={self.format}"
        ]
        
        return f"{base_url}?{'&'.join(params)}"
    
    def _tile_to_bbox(self, x: int, y: int, z: int) -> str:
        """
        Convert tile coordinates to Web Mercator bbox.
        
        Args:
            x: Tile X coordinate
            y: Tile Y coordinate
            z: Tile Z (zoom) coordinate
            
        Returns:
            Bbox string "minx,miny,maxx,maxy"
        """
        n = 2 ** z
        
        # Web Mercator bounds
        mercator_max = 20037508.34
        
        min_x = (x / n) * 2 * mercator_max - mercator_max
        max_x = ((x + 1) / n) * 2 * mercator_max - mercator_max
        min_y = mercator_max - ((y + 1) / n) * 2 * mercator_max
        max_y = mercator_max - (y / n) * 2 * mercator_max
        
        return f"{min_x},{min_y},{max_x},{max_y}"


class ArcGISProvider(ImageryProvider):
    """ArcGIS REST API provider."""
    
    def get_tile_url(self, x: int, y: int, z: int) -> str:
        """
        Get URL for ArcGIS tile.
        
        ArcGIS format: https://example.com/tile/{z}/{y}/{x}
        
        Args:
            x: Tile X coordinate
            y: Tile Y coordinate
            z: Tile Z (zoom) coordinate
            
        Returns:
            Tile URL
        """
        url = self.config.url
        
        # Ensure proper format
        if not url.endswith('/'):
            url += '/'
        
        if '{z}' in url:
            url = url.replace('{z}', str(z))
            url = url.replace('{y}', str(y))
            url = url.replace('{x}', str(x))
        else:
            url = f"{url}tile/{z}/{y}/{x}"
        
        return url


class ImageryProviderFactory:
    """Factory for creating imagery providers."""
    
    @staticmethod
    def create(config: ImageryProviderConfig) -> Optional[ImageryProvider]:
        """
        Create imagery provider from configuration.
        
        Args:
            config: Provider configuration
            
        Returns:
            ImageryProvider instance or None if invalid type
        """
        logger = logging.getLogger(__name__)
        
        provider_type = config.type.lower()
        
        if provider_type == 'xyz':
            return XYZProvider(config)
        elif provider_type == 'wmts':
            return WMTSProvider(config)
        elif provider_type == 'wms':
            return WMSProvider(config)
        elif provider_type == 'arcgis':
            return ArcGISProvider(config)
        else:
            logger.error(f"Unknown provider type: {config.type}")
            return None
