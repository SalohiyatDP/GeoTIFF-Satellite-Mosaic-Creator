"""
Map preview widget (simplified version).
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

from app.core.models import Polygon


class MapPreviewWidget(QWidget):
    """Widget for displaying map preview."""
    
    def __init__(self, parent=None):
        """Initialize map preview widget."""
        super().__init__(parent)
        
        self.current_polygon = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup user interface."""
        layout = QVBoxLayout(self)
        
        title = QLabel("Map Preview")
        title.setStyleSheet("font-weight: bold; padding: 5px;")
        layout.addWidget(title)
        
        # Placeholder for map
        self.map_label = QLabel("Map preview will appear here\n\n(Interactive map requires additional libraries)")
        self.map_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.map_label.setStyleSheet("border: 1px solid #555555; background-color: #3c3c3c;")
        layout.addWidget(self.map_label)
        
        # Info label
        self.info_label = QLabel("No polygon loaded")
        layout.addWidget(self.info_label)
    
    def display_polygon(self, polygon: Polygon):
        """Display polygon on map."""
        self.current_polygon = polygon
        
        info_text = f"Polygon: {len(polygon.coordinates)} vertices"
        
        if polygon.is_valid:
            info_text += " ✓ Valid"
        else:
            info_text += " ✗ Invalid"
        
        self.info_label.setText(info_text)
        
        # TODO: Implement actual map rendering
        # This would require a mapping library like folium, leaflet, or matplotlib
        self.map_label.setText(
            f"Polygon Preview\n\n"
            f"Vertices: {len(polygon.coordinates)}\n"
            f"CRS: {polygon.crs}\n"
            f"Status: {'Valid' if polygon.is_valid else 'Invalid'}"
        )
    
    def clear(self):
        """Clear map preview."""
        self.current_polygon = None
        self.map_label.setText("Map preview will appear here\n\n(Interactive map requires additional libraries)")
        self.info_label.setText("No polygon loaded")
