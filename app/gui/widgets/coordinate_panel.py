"""
Coordinate input panel.
"""
import logging
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QPushButton, QTextEdit, QTableWidget, QTableWidgetItem,
    QComboBox, QLabel, QFileDialog, QMessageBox
)
from PyQt6.QtCore import pyqtSignal

from app.core.models import Coordinate
from app.services.coordinate_manager import CoordinateManager


class CoordinatePanel(QWidget):
    """Panel for coordinate input and management."""
    
    coordinates_updated = pyqtSignal(list)  # List[Coordinate]
    
    def __init__(self, parent=None):
        """Initialize coordinate panel."""
        super().__init__(parent)
        
        self.logger = logging.getLogger(__name__)
        self.coordinate_manager = CoordinateManager()
        self.coordinates = []
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup user interface."""
        layout = QVBoxLayout(self)
        
        # Input method selection
        method_group = QGroupBox("Input Method")
        method_layout = QVBoxLayout()
        
        button_layout = QHBoxLayout()
        
        self.manual_btn = QPushButton("Manual Entry")
        self.manual_btn.clicked.connect(self.show_manual_input)
        button_layout.addWidget(self.manual_btn)
        
        self.txt_btn = QPushButton("Import TXT")
        self.txt_btn.clicked.connect(self.import_txt)
        button_layout.addWidget(self.txt_btn)
        
        self.csv_btn = QPushButton("Import CSV")
        self.csv_btn.clicked.connect(self.import_csv)
        button_layout.addWidget(self.csv_btn)
        
        method_layout.addLayout(button_layout)
        
        button_layout2 = QHBoxLayout()
        
        self.shp_btn = QPushButton("Import Shapefile")
        self.shp_btn.clicked.connect(self.import_shapefile)
        button_layout2.addWidget(self.shp_btn)
        
        self.geojson_btn = QPushButton("Import GeoJSON")
        self.geojson_btn.clicked.connect(self.import_geojson)
        button_layout2.addWidget(self.geojson_btn)
        
        method_layout.addLayout(button_layout2)
        
        method_group.setLayout(method_layout)
        layout.addWidget(method_group)
        
        # CRS selection
        crs_group = QGroupBox("Coordinate System")
        crs_layout = QHBoxLayout()
        
        crs_layout.addWidget(QLabel("CRS:"))
        
        self.crs_combo = QComboBox()
        self.crs_combo.addItems([
            "EPSG:4326 (WGS84)",
            "EPSG:3857 (Web Mercator)",
            "EPSG:32632 (UTM Zone 32N)",
            "EPSG:32633 (UTM Zone 33N)"
        ])
        crs_layout.addWidget(self.crs_combo)
        
        crs_group.setLayout(crs_layout)
        layout.addWidget(crs_group)
        
        # Manual input area
        self.manual_group = QGroupBox("Manual Input")
        manual_layout = QVBoxLayout()
        
        manual_layout.addWidget(QLabel("Enter coordinates (one per line: x,y or lon,lat):"))
        
        self.coord_input = QTextEdit()
        self.coord_input.setPlaceholderText("Example:\n-73.9857, 40.7484\n-73.9667, 40.7831\n...")
        self.coord_input.setMaximumHeight(150)
        manual_layout.addWidget(self.coord_input)
        
        parse_btn = QPushButton("Parse Coordinates")
        parse_btn.clicked.connect(self.parse_manual_input)
        manual_layout.addWidget(parse_btn)
        
        self.manual_group.setLayout(manual_layout)
        self.manual_group.setVisible(False)
        layout.addWidget(self.manual_group)
        
        # Coordinates table
        table_group = QGroupBox("Coordinates")
        table_layout = QVBoxLayout()
        
        self.coord_table = QTableWidget()
        self.coord_table.setColumnCount(3)
        self.coord_table.setHorizontalHeaderLabels(["#", "X / Longitude", "Y / Latitude"])
        self.coord_table.horizontalHeader().setStretchLastSection(True)
        table_layout.addWidget(self.coord_table)
        
        table_btn_layout = QHBoxLayout()
        
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear)
        table_btn_layout.addWidget(clear_btn)
        
        apply_btn = QPushButton("Apply to Polygon")
        apply_btn.clicked.connect(self.apply_coordinates)
        table_btn_layout.addWidget(apply_btn)
        
        table_layout.addLayout(table_btn_layout)
        
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)
        
        layout.addStretch()
    
    def show_manual_input(self):
        """Show manual input area."""
        self.manual_group.setVisible(True)
    
    def parse_manual_input(self):
        """Parse manually entered coordinates."""
        text = self.coord_input.toPlainText()
        if not text.strip():
            QMessageBox.warning(self, "Warning", "Please enter coordinates")
            return
        
        crs = self._get_selected_crs()
        
        coords, errors = self.coordinate_manager.parse_manual_input(text, crs)
        
        if errors:
            error_text = "\n".join(errors[:10])  # Show first 10 errors
            if len(errors) > 10:
                error_text += f"\n... and {len(errors) - 10} more errors"
            QMessageBox.warning(self, "Parse Errors", error_text)
        
        if coords:
            self.coordinates = coords
            self._update_table()
            QMessageBox.information(
                self,
                "Success",
                f"Parsed {len(coords)} coordinates"
            )
    
    def import_txt(self):
        """Import coordinates from TXT file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import TXT File",
            str(Path.home()),
            "Text Files (*.txt);;All Files (*.*)"
        )
        
        if not file_path:
            return
        
        crs = self._get_selected_crs()
        coords, errors = self.coordinate_manager.load_from_txt(Path(file_path), crs)
        
        if errors:
            QMessageBox.warning(self, "Import Errors", "\n".join(errors[:5]))
        
        if coords:
            self.coordinates = coords
            self._update_table()
            QMessageBox.information(
                self,
                "Success",
                f"Imported {len(coords)} coordinates"
            )
    
    def import_csv(self):
        """Import coordinates from CSV file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import CSV File",
            str(Path.home()),
            "CSV Files (*.csv);;All Files (*.*)"
        )
        
        if not file_path:
            return
        
        crs = self._get_selected_crs()
        
        # TODO: Add dialog for column selection
        coords, errors = self.coordinate_manager.load_from_csv(
            Path(file_path),
            x_column="x",
            y_column="y",
            crs=crs
        )
        
        if errors:
            QMessageBox.warning(self, "Import Errors", "\n".join(errors[:5]))
        
        if coords:
            self.coordinates = coords
            self._update_table()
            QMessageBox.information(
                self,
                "Success",
                f"Imported {len(coords)} coordinates"
            )
    
    def import_shapefile(self):
        """Import polygon from Shapefile."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Shapefile",
            str(Path.home()),
            "Shapefiles (*.shp);;All Files (*.*)"
        )
        
        if not file_path:
            return
        
        polygon, errors = self.coordinate_manager.load_from_shapefile(Path(file_path))
        
        if errors:
            QMessageBox.warning(self, "Import Errors", "\n".join(errors))
        
        if polygon:
            self.coordinates = polygon.coordinates
            self._update_table()
            QMessageBox.information(
                self,
                "Success",
                f"Imported polygon with {len(self.coordinates)} vertices"
            )
    
    def import_geojson(self):
        """Import polygon from GeoJSON."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import GeoJSON",
            str(Path.home()),
            "GeoJSON Files (*.geojson *.json);;All Files (*.*)"
        )
        
        if not file_path:
            return
        
        polygon, errors = self.coordinate_manager.load_from_geojson(Path(file_path))
        
        if errors:
            QMessageBox.warning(self, "Import Errors", "\n".join(errors))
        
        if polygon:
            self.coordinates = polygon.coordinates
            self._update_table()
            QMessageBox.information(
                self,
                "Success",
                f"Imported polygon with {len(self.coordinates)} vertices"
            )
    
    def apply_coordinates(self):
        """Apply coordinates to polygon."""
        if not self.coordinates:
            QMessageBox.warning(self, "Warning", "No coordinates to apply")
            return
        
        self.coordinates_updated.emit(self.coordinates)
    
    def clear(self):
        """Clear all coordinates."""
        self.coordinates = []
        self.coord_table.setRowCount(0)
        self.coord_input.clear()
    
    def _update_table(self):
        """Update coordinates table."""
        self.coord_table.setRowCount(len(self.coordinates))
        
        for i, coord in enumerate(self.coordinates):
            self.coord_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.coord_table.setItem(i, 1, QTableWidgetItem(f"{coord.x:.6f}"))
            self.coord_table.setItem(i, 2, QTableWidgetItem(f"{coord.y:.6f}"))
    
    def _get_selected_crs(self) -> str:
        """Get selected CRS code."""
        text = self.crs_combo.currentText()
        # Extract EPSG code
        return text.split()[0]
