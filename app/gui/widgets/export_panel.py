"""
Export settings panel.
"""
import logging
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QComboBox,
    QLabel, QCheckBox, QLineEdit, QPushButton,
    QFileDialog, QHBoxLayout
)

from app.core.models import OutputFormat, ExportSettings


class ExportPanel(QWidget):
    """Panel for export settings."""
    
    def __init__(self, parent=None):
        """Initialize export panel."""
        super().__init__(parent)
        
        self.logger = logging.getLogger(__name__)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup user interface."""
        layout = QVBoxLayout(self)
        
        # Output format
        format_group = QGroupBox("Output Format")
        format_layout = QVBoxLayout()
        
        format_layout.addWidget(QLabel("Format:"))
        
        self.format_combo = QComboBox()
        self.format_combo.addItems([
            "GeoTIFF",
            "TIFF",
            "JPEG2000",
            "PNG",
            "JPEG"
        ])
        format_layout.addWidget(self.format_combo)
        
        format_group.setLayout(format_layout)
        layout.addWidget(format_group)
        
        # Output path
        path_group = QGroupBox("Output Path")
        path_layout = QVBoxLayout()
        
        path_row = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Select output file...")
        path_row.addWidget(self.path_edit)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_output)
        path_row.addWidget(browse_btn)
        
        path_layout.addLayout(path_row)
        path_group.setLayout(path_layout)
        layout.addWidget(path_group)
        
        # Options
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout()
        
        self.clip_check = QCheckBox("Clip to polygon boundary")
        self.clip_check.setChecked(True)
        options_layout.addWidget(self.clip_check)
        
        self.full_extent_check = QCheckBox("Also export full extent")
        options_layout.addWidget(self.full_extent_check)
        
        self.overviews_check = QCheckBox("Build internal overviews")
        self.overviews_check.setChecked(True)
        options_layout.addWidget(self.overviews_check)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        layout.addStretch()
    
    def browse_output(self):
        """Browse for output file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Output File",
            str(Path.home()),
            "GeoTIFF Files (*.tif *.tiff);;All Files (*.*)"
        )
        
        if file_path:
            self.path_edit.setText(file_path)
    
    def get_export_settings(self) -> ExportSettings:
        """Get export settings."""
        format_map = {
            "GeoTIFF": OutputFormat.GEOTIFF,
            "TIFF": OutputFormat.TIFF,
            "JPEG2000": OutputFormat.JPEG2000,
            "PNG": OutputFormat.PNG,
            "JPEG": OutputFormat.JPEG
        }
        
        return ExportSettings(
            output_format=format_map[self.format_combo.currentText()],
            clip_to_polygon=self.clip_check.isChecked(),
            export_full_extent=self.full_extent_check.isChecked(),
            build_overviews=self.overviews_check.isChecked()
        )
    
    def get_output_path(self) -> Path:
        """Get output file path."""
        return Path(self.path_edit.text()) if self.path_edit.text() else None
    
    def clear(self):
        """Clear settings."""
        self.path_edit.clear()
        self.clip_check.setChecked(True)
        self.full_extent_check.setChecked(False)
        self.overviews_check.setChecked(True)
