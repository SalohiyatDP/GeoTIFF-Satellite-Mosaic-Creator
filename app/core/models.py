"""
Domain models for the application.
"""
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Any
from enum import Enum
from datetime import datetime
from pathlib import Path
import json


class CoordinateSystem(Enum):
    """Supported coordinate systems."""
    WGS84 = "EPSG:4326"
    WGS84_PSEUDO_MERCATOR = "EPSG:3857"
    UTM_ZONE_32N = "EPSG:32632"
    UTM_ZONE_33N = "EPSG:32633"
    CUSTOM = "CUSTOM"


class OutputFormat(Enum):
    """Supported output formats."""
    GEOTIFF = "GTiff"
    TIFF = "TIFF"
    JPEG2000 = "JP2OpenJPEG"
    PNG = "PNG"
    JPEG = "JPEG"


class ProcessingStatus(Enum):
    """Processing status."""
    PENDING = "pending"
    VALIDATING = "validating"
    CALCULATING = "calculating"
    DOWNLOADING = "downloading"
    MOSAICKING = "mosaicking"
    CLIPPING = "clipping"
    EXPORTING = "exporting"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Coordinate:
    """A geographic coordinate."""
    x: float  # longitude or easting
    y: float  # latitude or northing
    crs: str = "EPSG:4326"
    
    def to_tuple(self) -> Tuple[float, float]:
        """Convert to tuple."""
        return (self.x, self.y)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {"x": self.x, "y": self.y, "crs": self.crs}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Coordinate':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class Polygon:
    """A polygon defined by coordinates."""
    coordinates: List[Coordinate]
    crs: str = "EPSG:4326"
    name: Optional[str] = None
    is_valid: bool = False
    validation_errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "coordinates": [c.to_dict() for c in self.coordinates],
            "crs": self.crs,
            "name": self.name,
            "is_valid": self.is_valid,
            "validation_errors": self.validation_errors
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Polygon':
        """Create from dictionary."""
        data['coordinates'] = [Coordinate.from_dict(c) for c in data['coordinates']]
        return cls(**data)


@dataclass
class BoundingBox:
    """A geographic bounding box."""
    min_x: float
    min_y: float
    max_x: float
    max_y: float
    crs: str = "EPSG:4326"
    
    def to_tuple(self) -> Tuple[float, float, float, float]:
        """Convert to tuple (minx, miny, maxx, maxy)."""
        return (self.min_x, self.min_y, self.max_x, self.max_y)
    
    def width(self) -> float:
        """Get width."""
        return self.max_x - self.min_x
    
    def height(self) -> float:
        """Get height."""
        return self.max_y - self.min_y
    
    def center(self) -> Coordinate:
        """Get center coordinate."""
        return Coordinate(
            x=(self.min_x + self.max_x) / 2,
            y=(self.min_y + self.max_y) / 2,
            crs=self.crs
        )


@dataclass
class TileInfo:
    """Information about a map tile."""
    x: int
    y: int
    z: int
    url: str
    downloaded: bool = False
    file_path: Optional[Path] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "url": self.url,
            "downloaded": self.downloaded,
            "file_path": str(self.file_path) if self.file_path else None
        }


@dataclass
class DownloadProgress:
    """Download progress information."""
    total_tiles: int
    downloaded_tiles: int
    failed_tiles: int
    current_tile: Optional[TileInfo] = None
    speed_mbps: float = 0.0
    estimated_time_remaining: Optional[float] = None  # seconds
    
    @property
    def percentage(self) -> float:
        """Get completion percentage."""
        if self.total_tiles == 0:
            return 0.0
        return (self.downloaded_tiles / self.total_tiles) * 100


@dataclass
class ExportSettings:
    """Settings for GeoTIFF export."""
    output_format: OutputFormat = OutputFormat.GEOTIFF
    compression: str = "LZW"
    build_overviews: bool = True
    clip_to_polygon: bool = True
    export_full_extent: bool = False
    target_crs: Optional[str] = None  # If None, use source CRS
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "output_format": self.output_format.value,
            "compression": self.compression,
            "build_overviews": self.build_overviews,
            "clip_to_polygon": self.clip_to_polygon,
            "export_full_extent": self.export_full_extent,
            "target_crs": self.target_crs
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExportSettings':
        """Create from dictionary."""
        data['output_format'] = OutputFormat(data['output_format'])
        return cls(**data)


@dataclass
class Project:
    """A mosaic creation project."""
    name: str
    polygon: Polygon
    imagery_provider: str
    zoom_level: int
    export_settings: ExportSettings
    output_path: Optional[Path] = None
    status: ProcessingStatus = ProcessingStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    bounding_box: Optional[BoundingBox] = None
    tiles: List[TileInfo] = field(default_factory=list)
    download_progress: Optional[DownloadProgress] = None
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "polygon": self.polygon.to_dict(),
            "imagery_provider": self.imagery_provider,
            "zoom_level": self.zoom_level,
            "export_settings": self.export_settings.to_dict(),
            "output_path": str(self.output_path) if self.output_path else None,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "bounding_box": {
                "min_x": self.bounding_box.min_x,
                "min_y": self.bounding_box.min_y,
                "max_x": self.bounding_box.max_x,
                "max_y": self.bounding_box.max_y,
                "crs": self.bounding_box.crs
            } if self.bounding_box else None,
            "error_message": self.error_message
        }
    
    def save(self, path: Path):
        """Save project to file."""
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, path: Path) -> 'Project':
        """Load project from file."""
        with open(path, 'r') as f:
            data = json.load(f)
        
        # Convert back to objects
        data['polygon'] = Polygon.from_dict(data['polygon'])
        data['export_settings'] = ExportSettings.from_dict(data['export_settings'])
        data['status'] = ProcessingStatus(data['status'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        if data['output_path']:
            data['output_path'] = Path(data['output_path'])
        
        if data['bounding_box']:
            data['bounding_box'] = BoundingBox(**data['bounding_box'])
        
        return cls(**data)
