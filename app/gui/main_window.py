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
from app.gui.widgets.interactive_map import InteractiveMapWidget
from app.core.config import ConfigManager
from app.core.models import Project
from app.core.translations import t, get_translator


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
        self.setWindowTitle(t("app.title"))
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
        left_tabs.addTab(self.coordinate_panel, t("tabs.coordinates"))
        left_tabs.addTab(self.polygon_panel, t("tabs.polygon"))
        left_tabs.addTab(self.imagery_panel, t("tabs.imagery"))
        left_tabs.addTab(self.download_panel, t("tabs.download"))
        left_tabs.addTab(self.export_panel, t("tabs.export"))
        
        # Right side - Map preview and console
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(5)
        
        # Interactive map
        self.map_preview = InteractiveMapWidget()
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
        file_menu = menubar.addMenu(t("menu.file.title"))
        
        new_action = QAction(t("menu.file.new"), self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)
        
        open_action = QAction(t("menu.file.open"), self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_project)
        file_menu.addAction(open_action)
        
        save_action = QAction(t("menu.file.save"), self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)
        
        save_as_action = QAction(t("menu.file.save_as"), self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_project_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction(t("menu.file.exit"), self)
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu(t("menu.edit.title"))
        
        settings_action = QAction(t("menu.edit.settings"), self)
        settings_action.triggered.connect(self.show_settings)
        edit_menu.addAction(settings_action)
        
        # View menu
        view_menu = menubar.addMenu(t("menu.view.title"))
        
        dark_theme_action = QAction(t("menu.view.dark_theme"), self)
        dark_theme_action.triggered.connect(lambda: self.change_theme("dark"))
        view_menu.addAction(dark_theme_action)
        
        light_theme_action = QAction(t("menu.view.light_theme"), self)
        light_theme_action.triggered.connect(lambda: self.change_theme("light"))
        view_menu.addAction(light_theme_action)
        
        # Help menu
        help_menu = menubar.addMenu(t("menu.help.title"))
        
        about_action = QAction(t("menu.help.about"), self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        user_guide_action = QAction(t("menu.help.user_guide"), self)
        user_guide_action.triggered.connect(self.show_user_guide)
        help_menu.addAction(user_guide_action)
    
    def _setup_toolbar(self):
        """Setup toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # New project
        new_action = QAction(t("toolbar.new"), self)
        new_action.setToolTip(t("menu.file.new") + " (Ctrl+N)")
        new_action.triggered.connect(self.new_project)
        toolbar.addAction(new_action)
        
        # Open project
        open_action = QAction(t("toolbar.open"), self)
        open_action.setToolTip(t("menu.file.open") + " (Ctrl+O)")
        open_action.triggered.connect(self.open_project)
        toolbar.addAction(open_action)
        
        # Save project
        save_action = QAction(t("toolbar.save"), self)
        save_action.setToolTip(t("menu.file.save") + " (Ctrl+S)")
        save_action.triggered.connect(self.save_project)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        # Start processing
        self.start_action = QAction(t("toolbar.start"), self)
        self.start_action.setToolTip(t("toolbar.start"))
        self.start_action.triggered.connect(self.start_processing)
        toolbar.addAction(self.start_action)
        
        # Stop processing
        self.stop_action = QAction(t("toolbar.stop"), self)
        self.stop_action.setToolTip(t("toolbar.stop"))
        self.stop_action.triggered.connect(self.stop_processing)
        self.stop_action.setEnabled(False)
        toolbar.addAction(self.stop_action)
    
    def _setup_statusbar(self):
        """Setup status bar."""
        self.statusBar().showMessage(t("app.ready"))
    
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
                t("messages.new_project"),
                t("messages.current_project_close"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.No:
                return
        
        # Reset all panels
        self.coordinate_panel.clear()
        self.polygon_panel.clear()
        self.download_panel.clear()
        self.export_panel.clear()
        self.map_preview.clear_map()
        
        self.current_project = None
        self.statusBar().showMessage(t("messages.new_project_created"))
        self.logger.info("New project created")
    
    def open_project(self):
        """Open existing project."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            t("messages.open_project"),
            str(Path.home()),
            t("messages.project_files")
        )
        
        if not file_path:
            return
        
        try:
            project = Project.load(Path(file_path))
            self.current_project = project
            
            # Load project data into panels
            # TODO: Implement project loading
            
            self.statusBar().showMessage(t("messages.project_opened").format(path=file_path))
            self.logger.info(f"Project opened: {file_path}")
            
        except Exception as e:
            QMessageBox.critical(
                self,
                t("polygon_panel.error"),
                t("errors.failed_to_open").format(error=str(e))
            )
            self.logger.error(f"Failed to open project: {str(e)}")
    
    def save_project(self):
        """Save current project."""
        if self.current_project is None:
            self.save_project_as()
            return
        
        # TODO: Implement project saving
        self.statusBar().showMessage(t("messages.project_saved"))
        self.logger.info("Project saved")
    
    def save_project_as(self):
        """Save project with new name."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            t("messages.save_project_as"),
            str(Path.home()),
            t("messages.project_files")
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
        self.statusBar().showMessage(t("messages.processing_started"))
        
        # TODO: Implement processing workflow
        
        self.logger.info("Processing started")
    
    def stop_processing(self):
        """Stop processing."""
        self.start_action.setEnabled(True)
        self.stop_action.setEnabled(False)
        self.statusBar().showMessage(t("messages.processing_stopped"))
        
        # TODO: Implement stop logic
        
        self.logger.info("Processing stopped")
    
    def show_settings(self):
        """Show settings dialog."""
        # TODO: Implement settings dialog
        QMessageBox.information(
            self,
            t("messages.settings"),
            t("messages.settings_not_implemented")
        )
    
    def change_theme(self, theme: str):
        """Change application theme."""
        self.config_manager.config.theme = theme
        self.config_manager.save()
        self._apply_theme()
        self.statusBar().showMessage(t("messages.theme_changed").format(theme=theme))
        self.logger.info(f"Theme changed to {theme}")
    
    def show_about(self):
        """Show about dialog."""
        from app import __version__
        
        QMessageBox.about(
            self,
            t("messages.about"),
            f"<h2>{t('app.title')}</h2>"
            f"<p>Versiya {__version__}</p>"
            f"<p>Sun'iy yo'ldosh tasvirlaridan georeferenslangan mozaikalar yaratish uchun professional GIS dasturi.</p>"
            f"<p><b>Imkoniyatlar:</b></p>"
            f"<ul>"
            f"<li>Turli xil koordinata kiritish formatlari</li>"
            f"<li>Avtomatik plitka hisoblash va yuklab olish</li>"
            f"<li>Yaxlit mozaika yaratish</li>"
            f"<li>Ko'pburchakka kesish</li>"
            f"<li>ArcGIS-mos GeoTIFF eksport</li>"
            f"<li>Interaktiv xaritada polygon chizish</li>"
            f"</ul>"
        )
    
    def show_user_guide(self):
        """Show user guide."""
        # TODO: Implement user guide
        QMessageBox.information(
            self,
            t("messages.user_guide"),
            t("messages.guide_not_implemented")
        )
    
    def closeEvent(self, event):
        """Handle window close event."""
        if self.current_project:
            reply = QMessageBox.question(
                self,
                t("messages.exit_save"),
                t("messages.save_before_exit"),
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
