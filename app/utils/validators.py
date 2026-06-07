"""
Validation utilities.
"""
from typing import List, Tuple
import re


def validate_coordinate(lat: float, lon: float) -> Tuple[bool, str]:
    """
    Validate WGS84 coordinate.
    
    Args:
        lat: Latitude
        lon: Longitude
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not -90 <= lat <= 90:
        return False, f"Latitude {lat} out of range [-90, 90]"
    
    if not -180 <= lon <= 180:
        return False, f"Longitude {lon} out of range [-180, 180]"
    
    return True, ""


def validate_epsg_code(epsg: str) -> Tuple[bool, str]:
    """
    Validate EPSG code format.
    
    Args:
        epsg: EPSG code string (e.g., "EPSG:4326")
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    pattern = r'^EPSG:\d+$'
    if not re.match(pattern, epsg):
        return False, f"Invalid EPSG format: {epsg}. Expected format: EPSG:####"
    
    return True, ""


def validate_zoom_level(zoom: int, max_zoom: int = 19) -> Tuple[bool, str]:
    """
    Validate zoom level.
    
    Args:
        zoom: Zoom level
        max_zoom: Maximum allowed zoom level
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not 0 <= zoom <= max_zoom:
        return False, f"Zoom level {zoom} out of range [0, {max_zoom}]"
    
    return True, ""


def validate_file_path(path: str, must_exist: bool = False) -> Tuple[bool, str]:
    """
    Validate file path.
    
    Args:
        path: File path
        must_exist: Whether file must exist
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    from pathlib import Path
    
    try:
        p = Path(path)
        
        if must_exist and not p.exists():
            return False, f"File does not exist: {path}"
        
        return True, ""
    except Exception as e:
        return False, f"Invalid file path: {str(e)}"


def validate_url(url: str) -> Tuple[bool, str]:
    """
    Validate URL.
    
    Args:
        url: URL string
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    pattern = r'^https?://.+'
    if not re.match(pattern, url):
        return False, f"Invalid URL format: {url}"
    
    return True, ""
