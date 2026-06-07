"""
Application configuration management.
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class ImageryProviderConfig:
    """Configuration for an imagery provider."""
    name: str
    type: str  # 'xyz', 'wmts', 'wms', 'arcgis'
    url: str
    max_zoom: int
    attribution: str
    headers: Optional[Dict[str, str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ImageryProviderConfig':
        return cls(**data)


@dataclass
class AppConfig:
    """Main application configuration."""
    # Paths
    cache_dir: str = "cache"
    projects_dir: str = "projects"
    logs_dir: str = "logs"
    
    # Download settings
    max_concurrent_downloads: int = 10
    download_timeout: int = 30
    max_retries: int = 3
    
    # Processing settings
    default_zoom_level: int = 18
    tile_size: int = 256
    compression_type: str = "LZW"
    build_overviews: bool = True
    
    # UI settings
    theme: str = "dark"  # 'dark' or 'light'
    map_preview_zoom: int = 12
    
    # Default imagery provider
    default_provider: str = "OpenStreetMap"
    
    # Imagery providers
    imagery_providers: Dict[str, ImageryProviderConfig] = None
    
    def __post_init__(self):
        if self.imagery_providers is None:
            self.imagery_providers = self._default_providers()
    
    def _default_providers(self) -> Dict[str, ImageryProviderConfig]:
        """Get default imagery providers."""
        return {
            "OpenStreetMap": ImageryProviderConfig(
                name="OpenStreetMap",
                type="xyz",
                url="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                max_zoom=19,
                attribution="© OpenStreetMap contributors"
            ),
            "Esri World Imagery": ImageryProviderConfig(
                name="Esri World Imagery",
                type="xyz",
                url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                max_zoom=19,
                attribution="© Esri"
            ),
            "CartoDB Positron": ImageryProviderConfig(
                name="CartoDB Positron",
                type="xyz",
                url="https://a.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png",
                max_zoom=19,
                attribution="© CartoDB, © OpenStreetMap contributors"
            ),
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        # Convert ImageryProviderConfig objects
        data['imagery_providers'] = {
            name: provider.to_dict() 
            for name, provider in self.imagery_providers.items()
        }
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AppConfig':
        """Create from dictionary."""
        # Convert imagery providers
        if 'imagery_providers' in data:
            data['imagery_providers'] = {
                name: ImageryProviderConfig.from_dict(provider)
                for name, provider in data['imagery_providers'].items()
            }
        return cls(**data)
    
    def save(self, path: Path):
        """Save configuration to file."""
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, path: Path) -> 'AppConfig':
        """Load configuration from file."""
        with open(path, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)


class ConfigManager:
    """Manages application configuration."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file
        """
        if config_path is None:
            config_path = Path.home() / ".geotiff_mosaic" / "config.json"
        
        self.config_path = config_path
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load or create config
        if self.config_path.exists():
            self.config = AppConfig.load(self.config_path)
        else:
            self.config = AppConfig()
            self.save()
    
    def save(self):
        """Save current configuration."""
        self.config.save(self.config_path)
    
    def get_provider(self, name: str) -> Optional[ImageryProviderConfig]:
        """Get imagery provider by name."""
        return self.config.imagery_providers.get(name)
    
    def add_provider(self, provider: ImageryProviderConfig):
        """Add or update imagery provider."""
        self.config.imagery_providers[provider.name] = provider
        self.save()
    
    def remove_provider(self, name: str):
        """Remove imagery provider."""
        if name in self.config.imagery_providers:
            del self.config.imagery_providers[name]
            self.save()
