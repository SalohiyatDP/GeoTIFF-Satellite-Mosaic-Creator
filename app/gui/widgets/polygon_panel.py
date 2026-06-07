"""
Polygon validation and management panel.
"""
import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QPushButton,
    QLabel, QMessageBox, QTextEdit
)
from PyQt6.QtCore import pyqtSignal

from app.core.models import Polygon, Coordinate
from app.services.polygon_engine import PolygonEngine
from app.services.coordinate_manager import CoordinateManager


class PolygonPanel(QWidget):
    """Panel for polygon validation and operations."""
    
    polygon_created = pyqtSignal(Polygon)
    
    def __init__(self, parent=None):
        """Initialize polygon panel."""
        super().__init__(parent)
        
        self.logger = logging.getLogger(__name__)
        self.polygon_engine = PolygonEngine()
        self.coordinate_manager = CoordinateManager()
        
        self.current_polygon = None
        self.coordinates = []
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup user interface."""
        layout = QVBoxLayout(self)
        
        # Info group
        info_group = QGroupBox("Polygon Information")
        info_layout = QVBoxLayout()
        
        self.info_label = QLabel("No polygon created")
        self.info_label.setWordWrap(True)
        info_layout.addWidget(self.info_label)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Actions group
        actions_group = QGroupBox("Actions")
        actions_layout = QVBoxLayout()
        
        self.create_btn = QPushButton("Create Polygon")
        self.create_btn.clicked.connect(self.create_polygon)
        self.create_btn.setEnabled(False)
        actions_layout.addWidget(self.create_btn)
        
        self.validate_btn = QPushButton("Validate Polygon")
        self.validate_btn.clicked.connect(self.validate_polygon)
        self.validate_btn.setEnabled(False)
        actions_layout.addWidget(self.validate_btn)
        
        self.fix_btn = QPushButton("Auto-Fix Issues")
        self.fix_btn.clicked.connect(self.fix_polygon)
        self.fix_btn.setEnabled(False)
        actions_layout.addWidget(self.fix_btn)
        
        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)
        
        # Validation results
        validation_group = QGroupBox("Validation Results")
        validation_layout = QVBoxLayout()
        
        self.validation_text = QTextEdit()
        self.validation_text.setReadOnly(True)
        self.validation_text.setMaximumHeight(150)
        validation_layout.addWidget(self.validation_text)
        
        validation_group.setLayout(validation_layout)
        layout.addWidget(validation_group)
        
        layout.addStretch()
    
    def update_coordinates(self, coordinates: list):
        """
        Update coordinates from coordinate panel.
        
        Args:
            coordinates: List of Coordinate objects
        """
        self.coordinates = coordinates
        self.create_btn.setEnabled(len(coordinates) >= 3)
        self.info_label.setText(f"Ready to create polygon with {len(coordinates)} vertices")
        self.logger.info(f"Received {len(coordinates)} coordinates")
    
    def create_polygon(self):
        """Create polygon from coordinates."""
        if len(self.coordinates) < 3:
            QMessageBox.warning(
                self,
                "Insufficient Coordinates",
                "At least 3 coordinates are required to create a polygon"
            )
            return
        
        try:
            self.current_polygon = self.coordinate_manager.create_polygon_from_coordinates(
                self.coordinates,
                name="User Polygon"
            )
            
            # Auto-close polygon
            self.current_polygon = self.polygon_engine.close_polygon(self.current_polygon)
            
            # Update UI
            self.info_label.setText(
                f"Polygon created with {len(self.current_polygon.coordinates)} vertices"
            )
            
            self.validate_btn.setEnabled(True)
            self.fix_btn.setEnabled(True)
            
            # Auto-validate
            self.validate_polygon()
            
            # Emit signal
            self.polygon_created.emit(self.current_polygon)
            
            self.logger.info("Polygon created successfully")
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to create polygon: {str(e)}"
            )
            self.logger.error(f"Failed to create polygon: {str(e)}")
    
    def validate_polygon(self):
        """Validate current polygon."""
        if self.current_polygon is None:
            return
        
        is_valid, errors = self.polygon_engine.validate_polygon(self.current_polygon)
        
        self.current_polygon.is_valid = is_valid
        self.current_polygon.validation_errors = errors
        
        if is_valid:
            self.validation_text.setPlainText("✓ Polygon is valid!")
            
            # Calculate additional info
            bbox = self.polygon_engine.calculate_bounding_box(self.current_polygon)
            area = self.polygon_engine.get_polygon_area(self.current_polygon)
            centroid = self.polygon_engine.get_polygon_centroid(self.current_polygon)
            
            info_text = f"✓ Polygon is valid!\n\n"
            info_text += f"Vertices: {len(self.current_polygon.coordinates)}\n"
            
            if bbox:
                info_text += f"Bounding Box:\n"
                info_text += f"  Min X: {bbox.min_x:.6f}\n"
                info_text += f"  Min Y: {bbox.min_y:.6f}\n"
                info_text += f"  Max X: {bbox.max_x:.6f}\n"
                info_text += f"  Max Y: {bbox.max_y:.6f}\n"
            
            if area:
                info_text += f"Area: {area:.6f} square degrees\n"
            
            if centroid:
                info_text += f"Centroid: ({centroid.x:.6f}, {centroid.y:.6f})\n"
            
            self.validation_text.setPlainText(info_text)
            
        else:
            error_text = "✗ Polygon validation failed:\n\n"
            error_text += "\n".join(f"• {error}" for error in errors)
            self.validation_text.setPlainText(error_text)
        
        self.logger.info(f"Polygon validation: {'valid' if is_valid else 'invalid'}")
    
    def fix_polygon(self):
        """Attempt to fix polygon issues."""
        if self.current_polygon is None:
            return
        
        fixed_polygon, errors = self.polygon_engine.fix_self_intersections(self.current_polygon)
        
        if fixed_polygon:
            self.current_polygon = fixed_polygon
            self.validate_polygon()
            
            QMessageBox.information(
                self,
                "Success",
                "Polygon issues have been automatically fixed!"
            )
            
            # Emit updated polygon
            self.polygon_created.emit(self.current_polygon)
            
            self.logger.info("Polygon fixed successfully")
        else:
            error_text = "Failed to fix polygon:\n\n" + "\n".join(errors)
            QMessageBox.warning(self, "Fix Failed", error_text)
            self.logger.warning("Failed to fix polygon")
    
    def clear(self):
        """Clear polygon data."""
        self.current_polygon = None
        self.coordinates = []
        self.info_label.setText("No polygon created")
        self.validation_text.clear()
        self.create_btn.setEnabled(False)
        self.validate_btn.setEnabled(False)
        self.fix_btn.setEnabled(False)
