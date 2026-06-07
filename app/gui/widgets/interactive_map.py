"""
Interactive map widget with Folium for polygon drawing.
Xaritada polygon chizish uchun interaktiv widget.
"""
import logging
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple
import json

try:
    import folium
    from folium import plugins
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import pyqtSignal, QUrl, Qt

from app.core.models import Coordinate, Polygon
from app.core.translations import t


class InteractiveMapWidget(QWidget):
    """
    Interactive map widget using Folium.
    Folium yordamida interaktiv xarita widget'i.
    
    Signals:
        polygon_drawn: Emitted when user draws a polygon on map
        polygon_edited: Emitted when user edits existing polygon
    """
    
    polygon_drawn = pyqtSignal(list)  # List[Coordinate]
    polygon_edited = pyqtSignal(list)  # List[Coordinate]
    
    def __init__(self, parent=None):
        """Initialize interactive map widget."""
        super().__init__(parent)
        
        self.logger = logging.getLogger(__name__)
        self.current_polygon = None
        self.map_center = [41.2995, 69.2401]  # Toshkent markazida
        self.zoom_level = 12
        
        self._setup_ui()
        
        if FOLIUM_AVAILABLE:
            self._create_map()
        else:
            self.logger.warning("Folium not available - map features disabled")
    
    def _setup_ui(self):
        """Setup user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Title and controls
        controls_layout = QHBoxLayout()
        
        title = QLabel(t("map_preview.title"))
        title.setStyleSheet("font-weight: bold; padding: 5px;")
        controls_layout.addWidget(title)
        
        controls_layout.addStretch()
        
        # Base map selector
        self.basemap_combo = QComboBox()
        self.basemap_combo.addItems([
            "OpenStreetMap",
            "Esri WorldImagery",
            "CartoDB Positron",
            "CartoDB Dark Matter"
        ])
        self.basemap_combo.currentTextChanged.connect(self._change_basemap)
        controls_layout.addWidget(QLabel("Xarita:"))
        controls_layout.addWidget(self.basemap_combo)
        
        # Clear button
        self.clear_btn = QPushButton("Tozalash")
        self.clear_btn.clicked.connect(self.clear_map)
        controls_layout.addWidget(self.clear_btn)
        
        layout.addLayout(controls_layout)
        
        # Map view
        if FOLIUM_AVAILABLE:
            self.map_view = QWebEngineView()
            layout.addWidget(self.map_view)
            
            # Instructions
            instructions = QLabel(t("map_preview.draw_instructions"))
            instructions.setWordWrap(True)
            instructions.setStyleSheet("padding: 5px; font-size: 9pt;")
            layout.addWidget(instructions)
        else:
            placeholder = QLabel(
                "Folium kutubxonasi o'rnatilmagan.\n\n"
                "O'rnatish: pip install folium\n\n"
                "Interaktiv xarita funksiyalari mavjud bo'lmaydi."
            )
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            placeholder.setStyleSheet("border: 1px solid #555555; padding: 20px;")
            layout.addWidget(placeholder)
    
    def _create_map(self):
        """Create Folium map with drawing tools."""
        if not FOLIUM_AVAILABLE:
            return
        
        try:
            # Create map centered on Tashkent
            m = folium.Map(
                location=self.map_center,
                zoom_start=self.zoom_level,
                tiles=None,
                control_scale=True
            )
            
            # Add base layer
            self._add_basemap(m, self.basemap_combo.currentText())
            
            # Add drawing tools
            draw = plugins.Draw(
                export=True,
                filename='polygon.geojson',
                position='topleft',
                draw_options={
                    'polyline': False,
                    'rectangle': True,
                    'circle': False,
                    'marker': False,
                    'circlemarker': False,
                    'polygon': {
                        'allowIntersection': False,
                        'drawError': {
                            'color': '#e1e100',
                            'message': "Ko'pburchak o'zini kesib o'tmaydi!"
                        },
                        'shapeOptions': {
                            'color': '#0e639c',
                            'weight': 3,
                            'fillOpacity': 0.3
                        }
                    }
                },
                edit_options={
                    'featureGroup': folium.FeatureGroup().add_to(m)
                }
            )
            draw.add_to(m)
            
            # Add fullscreen control
            plugins.Fullscreen(
                position='topright',
                title='To\'liq ekran',
                title_cancel='Chiqish',
                force_separate_button=True
            ).add_to(m)
            
            # Add geocoder for search
            plugins.Geocoder(
                collapsed=True,
                position='topright',
                placeholder='Joyni qidirish...'
            ).add_to(m)
            
            # Add measure control
            plugins.MeasureControl(
                position='bottomleft',
                primary_length_unit='meters',
                secondary_length_unit='kilometers',
                primary_area_unit='sqmeters',
                secondary_area_unit='hectares'
            ).add_to(m)
            
            # Add layer control
            folium.LayerControl().add_to(m)
            
            # Add custom JavaScript to capture drawn polygons
            draw_js = """
            <script>
            window.addEventListener('load', function() {
                map.on('draw:created', function (e) {
                    var layer = e.layer;
                    var coords = layer.getLatLngs()[0];
                    var coordsList = coords.map(function(c) {
                        return [c.lng, c.lat];
                    });
                    
                    // Send to PyQt
                    console.log('Polygon drawn:', coordsList);
                    
                    // Store in window for PyQt to access
                    window.drawnPolygon = coordsList;
                });
                
                map.on('draw:edited', function (e) {
                    var layers = e.layers;
                    layers.eachLayer(function (layer) {
                        var coords = layer.getLatLngs()[0];
                        var coordsList = coords.map(function(c) {
                            return [c.lng, c.lat];
                        });
                        
                        console.log('Polygon edited:', coordsList);
                        window.editedPolygon = coordsList;
                    });
                });
            });
            </script>
            """
            
            # Save to temp file
            temp_file = tempfile.NamedTemporaryFile(
                mode='w', 
                suffix='.html', 
                delete=False,
                encoding='utf-8'
            )
            
            # Get HTML
            html = m.get_root().render()
            
            # Add custom JS
            html = html.replace('</body>', draw_js + '</body>')
            
            temp_file.write(html)
            temp_file.close()
            
            self.temp_file_path = temp_file.name
            
            # Load in QWebEngineView
            self.map_view.setUrl(QUrl.fromLocalFile(self.temp_file_path))
            
            self.logger.info("Interactive map created successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to create map: {str(e)}", exc_info=True)
    
    def _add_basemap(self, m: 'folium.Map', basemap_name: str):
        """Add basemap layer to map."""
        basemaps = {
            "OpenStreetMap": folium.TileLayer(
                tiles='OpenStreetMap',
                name='OpenStreetMap',
                overlay=False,
                control=True
            ),
            "Esri WorldImagery": folium.TileLayer(
                tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                attr='Esri',
                name='Esri WorldImagery',
                overlay=False,
                control=True
            ),
            "CartoDB Positron": folium.TileLayer(
                tiles='CartoDB positron',
                name='CartoDB Positron',
                overlay=False,
                control=True
            ),
            "CartoDB Dark Matter": folium.TileLayer(
                tiles='CartoDB dark_matter',
                name='CartoDB Dark Matter',
                overlay=False,
                control=True
            )
        }
        
        layer = basemaps.get(basemap_name, basemaps["OpenStreetMap"])
        layer.add_to(m)
    
    def _change_basemap(self, basemap_name: str):
        """Change base map layer."""
        self.logger.info(f"Changing basemap to: {basemap_name}")
        self._create_map()
    
    def display_polygon(self, polygon: Polygon):
        """
        Display polygon on map.
        
        Args:
            polygon: Polygon to display
        """
        if not FOLIUM_AVAILABLE:
            self.logger.warning("Folium not available")
            return
        
        self.current_polygon = polygon
        
        try:
            # Get coordinates
            coords = [(c.y, c.x) for c in polygon.coordinates]  # lat, lon
            
            if not coords:
                return
            
            # Calculate center
            lats = [c[0] for c in coords]
            lons = [c[1] for c in coords]
            self.map_center = [sum(lats) / len(lats), sum(lons) / len(lons)]
            
            # Create map
            m = folium.Map(
                location=self.map_center,
                zoom_start=13,
                tiles=None
            )
            
            # Add basemap
            self._add_basemap(m, self.basemap_combo.currentText())
            
            # Add polygon
            folium.Polygon(
                locations=coords,
                color='#0e639c',
                weight=3,
                fill=True,
                fillColor='#0e639c',
                fillOpacity=0.3,
                popup=f"Ko'pburchak: {len(coords)} uchlar"
            ).add_to(m)
            
            # Add markers at vertices
            for i, coord in enumerate(coords):
                folium.CircleMarker(
                    location=coord,
                    radius=5,
                    color='#0e639c',
                    fill=True,
                    popup=f"Uch {i+1}: ({coord[0]:.6f}, {coord[1]:.6f})"
                ).add_to(m)
            
            # Fit bounds
            m.fit_bounds([(min(lats), min(lons)), (max(lats), max(lons))])
            
            # Add controls
            folium.LayerControl().add_to(m)
            plugins.Fullscreen().add_to(m)
            
            # Save and load
            temp_file = tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.html',
                delete=False,
                encoding='utf-8'
            )
            m.save(temp_file.name)
            temp_file.close()
            
            self.temp_file_path = temp_file.name
            self.map_view.setUrl(QUrl.fromLocalFile(self.temp_file_path))
            
            self.logger.info(f"Displayed polygon with {len(coords)} vertices")
            
        except Exception as e:
            self.logger.error(f"Failed to display polygon: {str(e)}", exc_info=True)
    
    def clear_map(self):
        """Clear map and reset to default."""
        self.current_polygon = None
        self.map_center = [41.2995, 69.2401]
        self.zoom_level = 12
        self._create_map()
        self.logger.info("Map cleared")
    
    def get_drawn_polygon(self) -> Optional[List[Coordinate]]:
        """
        Get polygon drawn by user.
        
        Returns:
            List of coordinates or None
        """
        # This would require JavaScript bridge to get data from map
        # For now, return None - will be implemented with JS communication
        return None
    
    def set_center(self, lat: float, lon: float, zoom: int = 12):
        """
        Set map center and zoom.
        
        Args:
            lat: Latitude
            lon: Longitude
            zoom: Zoom level
        """
        self.map_center = [lat, lon]
        self.zoom_level = zoom
        self._create_map()
