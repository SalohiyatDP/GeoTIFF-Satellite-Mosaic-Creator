"""
Project management service.
Handles project save/load and batch processing.
"""
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from PyQt6.QtCore import QObject, pyqtSignal

from app.core.models import Project, ProcessingStatus


class ProjectManager(QObject):
    """Manages projects and batch processing."""
    
    project_loaded = pyqtSignal(Project)
    project_saved = pyqtSignal(str)
    batch_progress = pyqtSignal(int, int)  # current, total
    
    def __init__(self):
        """Initialize project manager."""
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.current_project = None
        self.batch_queue = []
    
    def create_project(self, name: str) -> Project:
        """
        Create new project.
        
        Args:
            name: Project name
            
        Returns:
            New Project instance
        """
        from app.core.models import Polygon, ExportSettings
        
        project = Project(
            name=name,
            polygon=Polygon(coordinates=[], name=name),
            imagery_provider="OpenStreetMap",
            zoom_level=15,
            export_settings=ExportSettings()
        )
        
        self.current_project = project
        self.logger.info(f"Created new project: {name}")
        
        return project
    
    def save_project(self, project: Project, path: Path) -> bool:
        """
        Save project to file.
        
        Args:
            project: Project to save
            path: File path
            
        Returns:
            True if successful
        """
        try:
            project.updated_at = datetime.now()
            project.save(path)
            
            self.logger.info(f"Project saved: {path}")
            self.project_saved.emit(str(path))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save project: {str(e)}")
            return False
    
    def load_project(self, path: Path) -> Optional[Project]:
        """
        Load project from file.
        
        Args:
            path: File path
            
        Returns:
            Loaded Project or None
        """
        try:
            project = Project.load(path)
            self.current_project = project
            
            self.logger.info(f"Project loaded: {path}")
            self.project_loaded.emit(project)
            
            return project
            
        except Exception as e:
            self.logger.error(f"Failed to load project: {str(e)}")
            return None
    
    def add_to_batch_queue(self, project: Project):
        """
        Add project to batch processing queue.
        
        Args:
            project: Project to add
        """
        self.batch_queue.append(project)
        self.logger.info(f"Added project to batch queue: {project.name}")
    
    def remove_from_batch_queue(self, index: int):
        """
        Remove project from batch queue.
        
        Args:
            index: Queue index
        """
        if 0 <= index < len(self.batch_queue):
            project = self.batch_queue.pop(index)
            self.logger.info(f"Removed project from batch queue: {project.name}")
    
    def clear_batch_queue(self):
        """Clear batch processing queue."""
        self.batch_queue.clear()
        self.logger.info("Batch queue cleared")
    
    def get_batch_queue(self) -> List[Project]:
        """Get current batch queue."""
        return self.batch_queue.copy()
    
    def export_project_summary(self, project: Project, path: Path) -> bool:
        """
        Export project summary to text file.
        
        Args:
            project: Project to export
            path: Output file path
            
        Returns:
            True if successful
        """
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(f"GeoTIFF Mosaic Creator - Project Summary\n")
                f.write(f"{'=' * 50}\n\n")
                
                f.write(f"Project Name: {project.name}\n")
                f.write(f"Created: {project.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Updated: {project.updated_at.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Status: {project.status.value}\n\n")
                
                f.write(f"Polygon Information:\n")
                f.write(f"  Vertices: {len(project.polygon.coordinates)}\n")
                f.write(f"  CRS: {project.polygon.crs}\n")
                f.write(f"  Valid: {project.polygon.is_valid}\n\n")
                
                if project.bounding_box:
                    f.write(f"Bounding Box:\n")
                    f.write(f"  Min X: {project.bounding_box.min_x:.6f}\n")
                    f.write(f"  Min Y: {project.bounding_box.min_y:.6f}\n")
                    f.write(f"  Max X: {project.bounding_box.max_x:.6f}\n")
                    f.write(f"  Max Y: {project.bounding_box.max_y:.6f}\n\n")
                
                f.write(f"Imagery Settings:\n")
                f.write(f"  Provider: {project.imagery_provider}\n")
                f.write(f"  Zoom Level: {project.zoom_level}\n")
                f.write(f"  Tiles: {len(project.tiles)}\n\n")
                
                f.write(f"Export Settings:\n")
                f.write(f"  Format: {project.export_settings.output_format.value}\n")
                f.write(f"  Compression: {project.export_settings.compression}\n")
                f.write(f"  Clip to Polygon: {project.export_settings.clip_to_polygon}\n")
                f.write(f"  Build Overviews: {project.export_settings.build_overviews}\n\n")
                
                if project.output_path:
                    f.write(f"Output Path: {project.output_path}\n\n")
                
                if project.error_message:
                    f.write(f"Error Message:\n{project.error_message}\n")
            
            self.logger.info(f"Project summary exported: {path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export project summary: {str(e)}")
            return False
