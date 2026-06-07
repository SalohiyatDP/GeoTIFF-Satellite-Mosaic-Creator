"""
Logging configuration and utilities.
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


def setup_logging(log_dir: Optional[Path] = None, level: int = logging.INFO):
    """
    Set up application logging.
    
    Args:
        log_dir: Directory for log files
        level: Logging level
    """
    if log_dir is None:
        log_dir = Path.home() / ".geotiff_mosaic" / "logs"
    
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create log filename with timestamp
    log_file = log_dir / f"geotiff_mosaic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # File handler - detailed logs
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)
    
    # Console handler - simple logs
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)
    
    # Log startup
    logging.info(f"Logging initialized. Log file: {log_file}")
    
    return log_file


class LoggerMixin:
    """Mixin to add logger property to classes."""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        return logging.getLogger(self.__class__.__name__)
