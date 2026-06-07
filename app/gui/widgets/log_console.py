"""
Log console widget.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel
from PyQt6.QtCore import Qt


class LogConsole(QWidget):
    """Console widget for displaying log messages."""
    
    def __init__(self, parent=None):
        """Initialize log console."""
        super().__init__(parent)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("Log Console")
        title.setStyleSheet("font-weight: bold; padding: 5px;")
        layout.addWidget(title)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        layout.addWidget(self.log_text)
    
    def append_log(self, message: str):
        """Append log message."""
        self.log_text.append(message)
        
        # Auto-scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def clear(self):
        """Clear log console."""
        self.log_text.clear()
