"""
Download progress panel.
"""
import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QProgressBar,
    QLabel, QPushButton
)
from PyQt6.QtCore import pyqtSignal


class DownloadPanel(QWidget):
    """Panel for download progress tracking."""
    
    log_message = pyqtSignal(str)
    
    def __init__(self, parent=None):
        """Initialize download panel."""
        super().__init__(parent)
        
        self.logger = logging.getLogger(__name__)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup user interface."""
        layout = QVBoxLayout(self)
        
        # Progress group
        progress_group = QGroupBox("Download Progress")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready")
        progress_layout.addWidget(self.status_label)
        
        self.details_label = QLabel("")
        progress_layout.addWidget(self.details_label)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # Stats group
        stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout()
        
        self.stats_label = QLabel("No downloads yet")
        self.stats_label.setWordWrap(True)
        stats_layout.addWidget(self.stats_label)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        layout.addStretch()
    
    def update_progress(self, current: int, total: int, status: str = ""):
        """Update progress display."""
        if total > 0:
            percentage = int((current / total) * 100)
            self.progress_bar.setValue(percentage)
            self.status_label.setText(f"Downloaded: {current}/{total} tiles ({percentage}%)")
        
        if status:
            self.details_label.setText(status)
    
    def update_stats(self, stats: dict):
        """Update statistics display."""
        text = ""
        for key, value in stats.items():
            text += f"{key}: {value}\n"
        self.stats_label.setText(text)
    
    def clear(self):
        """Clear progress."""
        self.progress_bar.setValue(0)
        self.status_label.setText("Ready")
        self.details_label.setText("")
        self.stats_label.setText("No downloads yet")
