"""
Main application window.
"""
import logging
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QMenuBar, QMenu, QStatusBar, QSplitter,
    QMessageBox, QFileDialog, QToolBar
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QIcon

from app.gui.styles import get_theme
from app.gui.widgets.coordinate_panel import CoordinatePanel
from app.gui.widgets.polygon_panel import PolygonPanel
from app.gui.widgets.imagery_panel import ImageryPanel
from app.gui.widgets.download_panel import DownloadPanel
from app.gui.widgets.export_panel import ExportPanel
from app.gui.widgets.log_console import LogConsole
from app.gui.widgets.map_preview import MapPreviewWidget
from app.core.config import ConfigManager
from app.core.models import Project


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        """Initialize main window."""
        super().__init__()
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing main window")
        
        # Configuration
        self.config_manager = ConfigManager()
        
        # Current project
        self.current_project = None
        
        # Setup UI
        self._setup_ui()
        self._setup_menubar()
        self._setup_toolbar()
        self._setup_statusbar()
        self._apply_theme()
        
        # Connect signals
        self._connect_signals()
        
        self.logger.info("Main window initialized")
    
    def _setup_ui(self):
        """Setup user interface."""
        self.setWindowTitle("GeoTIFF Satellite Mosaic Creator")
        self.setGeometry(100, 100, 1400, 900)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # Create main splitter (left/right)
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - Control panels in tabs
        left_tabs = QTabWidget()
        
        # Create panels
        self.coordinate_panel = CoordinatePanel()
        self.polygon_panel = PolygonPanel()
        self.imagery_panel = ImageryPanel(self.config_manager)
        self.download_panel = DownloadPanel()
        self.export_panel = ExportPanel()
        
        # Add tabs
        left_tabs.addTab(self.coordinate_panel, "Coordinates")
        left_tabs.addTab(self.polygon_panel, "Polygon")
        left_tabs.addTab(self.imagery_panel, "Imagery")
        left_tabs.addTab(self.download_panel, "Download")
        left_tabs.addTab(self.export_panel, "Export")
        
        # Right side - Map preview and console
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(5)
        
        # Map preview
        self.map_preview = MapPreviewWidget()
        right_layout.addWidget(self.map_preview, stretch=3)
        
        # Log console
        self.log_console = LogConsole()
        right_layout.addWidget(self.log_console, stretch=1)
        
        # Add to splitter
        main_splitter.addWidget(left_tabs)
        main_splitter.addWidget(right_widget)
        
        # Set splitter sizes (30% left, 70% right)
        main_splitter.setSizes([400, 1000])
        
        main_layout.addWidget(main_splitter)
    
    def _setup_menubar(self):
        """Setup menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_action = QAction("&New Project", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)
        
        open_action = QAction("&Open Project...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_project)
        file_menu.addAction(open_action)
        
        save_action = QAction("&Save Project", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save Project &As...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_project_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        settings_action = QAction("&Settings...", self)
        settings_action.triggered.connect(self.show_settings)
        edit_menu.addAction(settings_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        dark_theme_action = QAction("&Dark Theme", self)
        dark_theme_action.triggered.connect(lambda: self.change_theme("dark"))
        view_menu.addAction(dark_theme_action)
        
        light_theme_action = QAction("&Light Theme", self)
        light_theme_action.triggered.connect(lambda: self.change_theme("light"))
        view_menu.addAction(light_theme_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        user_guide_action = QAction("&User Guide", self)
        user_guide_action.triggered.connect(self.show_user_guide)
        help_menu.addAction(user_guide_action)
    
    def _setup_toolbar(self):
        """Setup toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # New project
        new_action = QAction("New", self)
        new_action.setToolTip("New Project (Ctrl+N)")
        new_action.triggered.connect(self.new_project)
        toolbar.addAction(new_action)
        
        # Open project
        open_action = QAction("Open", self)
        open_action.setToolTip("Open Project (Ctrl+O)")
        open_action.triggered.connect(self.open_project)
        toolbar.addAction(open_action)
        
        # Save project
        save_action = QAction("Save", self)
        save_action.setToolTip("Save Project (Ctrl+S)")
        save_action.triggered.connect(self.save_project)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        # Start processing
        self.start_action = QAction("Start", self)
        self.start_action.setToolTip("Start Processing")
        self.start_action.triggered.connect(self.start_processing)
        toolbar.addAction(self.start_action)
        
        # Stop processing
        self.stop_action = QAction("Stop", self)
        self.stop_action.setToolTip("Stop Processing")
        self.stop_action.triggered.connect(self.stop_processing)
        self.stop_action.setEnabled(False)
        toolbar.addAction(self.stop_action)
    
    def _setup_statusbar(self):
        """Setup status bar."""
        self.statusBar().showMessage("Ready")
    
    def _apply_theme(self):
        """Apply theme to application."""
        theme = self.config_manager.config.theme
        stylesheet = get_theme(theme)
        self.setStyleSheet(stylesheet)
    
    def _connect_signals(self):
        """Connect signals between widgets."""
        # Coordinate panel -> Polygon panel
        self.coordinate_panel.coordinates_updated.connect(
            self.polygon_panel.update_coordinates
        )
        
        # Polygon panel -> Map preview
        self.polygon_panel.polygon_created.connect(
            self.map_preview.display_polygon
        )
        
        # Download panel -> Log console
        self.download_panel.log_message.connect(
            self.log_console.append_log
        )
    
    def new_project(self):
        """Create new project."""
        if self.current_project:
            reply = QMessageBox.question(
                self,
                "New Project",
                "Current project will be closed. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.No:
                return
        
        # Reset all panels
        self.coordinate_panel.clear()
        self.polygon_panel.clear()
        self.download_panel.clear()
        self.export_panel.clear()
        self.map_preview.clear()
        
        self.current_project = None
        self.statusBar().showMessage("New project created")
        self.logger.info("New project created")
    
    def open_project(self):
        """Open existing project."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Project",
            str(Path.home()),
            "Project Files (*.gmproj);;All Files (*.*)"
        )
        
        if not file_path:
            return
        
        try:
            project = Project.load(Path(file_path))
            self.current_project = project
            
            # Load project data into panels
            # TODO: Implement project loading
            
            self.statusBar().showMessage(f"Project opened: {file_path}")
            self.logger.info(f"Project opened: {file_path}")
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open project: {str(e)}"
            )
            self.logger.error(f"Failed to open project: {str(e)}")
    
    def save_project(self):
        """Save current project."""
        if self.current_project is None:
            self.save_project_as()
            return
        
        # TODO: Implement project saving
        self.statusBar().showMessage("Project saved")
        self.logger.info("Project saved")
    
    def save_project_as(self):
        """Save project with new name."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Project As",
            str(Path.home()),
            "Project Files (*.gmproj)"
        )
        
        if not file_path:
            return
        
        # TODO: Implement project saving
        self.statusBar().showMessage(f"Project saved: {file_path}")
        self.logger.info(f"Project saved: {file_path}")
    
    def start_processing(self):
        """Start mosaic generation processing."""
        self.start_action.setEnabled(False)
        self.stop_action.setEnabled(True)
        self.statusBar().showMessage("Processing started...")
        
        # TODO: Implement processing workflow
        
        self.logger.info("Processing started")
    
    def stop_processing(self):
        """Stop processing."""
        self.start_action.setEnabled(True)
        self.stop_action.setEnabled(False)
        self.statusBar().showMessage("Processing stopped")
        
        # TODO: Implement stop logic
        
        self.logger.info("Processing stopped")
    
    def show_settings(self):
        """Show settings dialog."""
        # TODO: Implement settings dialog
        QMessageBox.information(
            self,
            "Settings",
            "Settings dialog not yet implemented"
        )
    
    def change_theme(self, theme: str):
        """Change application theme."""
        self.config_manager.config.theme = theme
        self.config_manager.save()
        self._apply_theme()
        self.statusBar().showMessage(f"Theme changed to {theme}")
        self.logger.info(f"Theme changed to {theme}")
    
    def show_about(self):
        """Show about dialog."""
        from app import __version__
        
        QMessageBox.about(
            self,
            "About GeoTIFF Mosaic Creator",
            f"<h2>GeoTIFF Satellite Mosaic Creator</h2>"
            f"<p>Version {__version__}</p>"
            f"<p>A professional desktop GIS application for generating "
            f"georeferenced satellite image mosaics from polygon coordinates.</p>"
            f"<p><b>Features:</b></p>"
            f"<ul>"
            f"<li>Multiple coordinate input formats</li>"
            f"<li>Automatic tile calculation and download</li>"
            f"<li>Seamless mosaic generation</li>"
            f"<li>Polygon clipping</li>"
            f"<li>ArcGIS-compatible GeoTIFF export</li>"
            f"</ul>"
        )
    
    def show_user_guide(self):
        """Show user guide."""
        # TODO: Implement user guide
        QMessageBox.information(
            self,
            "User Guide",
            "User guide not yet implemented"
        )
    
    def closeEvent(self, event):
        """Handle window close event."""
        if self.current_project:
            reply = QMessageBox.question(
                self,
                "Exit",
                "Do you want to save the current project before exiting?",
                QMessageBox.StandardButton.Yes | 
                QMessageBox.StandardButton.No | 
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.save_project()
                event.accept()
            elif reply == QMessageBox.StandardButton.No:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
        
        self.logger.info("Application closed")
