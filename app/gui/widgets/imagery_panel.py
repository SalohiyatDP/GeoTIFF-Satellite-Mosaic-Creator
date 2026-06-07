"""
Imagery provider configuration panel.
"""
import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QComboBox,
    QLabel, QSpinBox, QHBoxLayout
)

from app.core.config import ConfigManager


class ImageryPanel(QWidget):
    """Panel for imagery provider configuration."""
    
    def __init__(self, config_manager: ConfigManager, parent=None):
        """Initialize imagery panel."""
        super().__init__(parent)
        
        self.logger = logging.getLogger(__name__)
        self.config_manager = config_manager
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup user interface."""
        layout = QVBoxLayout(self)
        
        # Provider selection
        provider_group = QGroupBox("Imagery Provider")
        provider_layout = QVBoxLayout()
        
        provider_layout.addWidget(QLabel("Select imagery source:"))
        
        self.provider_combo = QComboBox()
        self._load_providers()
        provider_layout.addWidget(self.provider_combo)
        
        provider_group.setLayout(provider_layout)
        layout.addWidget(provider_group)
        
        # Zoom level
        zoom_group = QGroupBox("Zoom Level")
        zoom_layout = QHBoxLayout()
        
        zoom_layout.addWidget(QLabel("Zoom:"))
        
        self.zoom_spin = QSpinBox()
        self.zoom_spin.setMinimum(1)
        self.zoom_spin.setMaximum(19)
        self.zoom_spin.setValue(self.config_manager.config.default_zoom_level)
        zoom_layout.addWidget(self.zoom_spin)
        
        zoom_layout.addWidget(QLabel("(Higher = more detail, more tiles)"))
        zoom_layout.addStretch()
        
        zoom_group.setLayout(zoom_layout)
        layout.addWidget(zoom_group)
        
        layout.addStretch()
    
    def _load_providers(self):
        """Load available imagery providers."""
        self.provider_combo.clear()
        
        for name in self.config_manager.config.imagery_providers.keys():
            self.provider_combo.addItem(name)
        
        # Set default
        default_provider = self.config_manager.config.default_provider
        index = self.provider_combo.findText(default_provider)
        if index >= 0:
            self.provider_combo.setCurrentIndex(index)
    
    def get_selected_provider(self) -> str:
        """Get selected provider name."""
        return self.provider_combo.currentText()
    
    def get_zoom_level(self) -> int:
        """Get selected zoom level."""
        return self.zoom_spin.value()
