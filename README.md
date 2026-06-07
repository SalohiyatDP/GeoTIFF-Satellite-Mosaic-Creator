# GeoTIFF Satellite Mosaic Creator

A professional Windows desktop GIS application for generating high-resolution georeferenced satellite image mosaics from polygon coordinates.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.12-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## 📋 Overview

GeoTIFF Satellite Mosaic Creator is a comprehensive desktop application designed for cadastral and geospatial professionals. It automates the process of downloading satellite imagery tiles and generating ArcGIS-compatible GeoTIFF mosaics for any polygon area of interest.

### Key Features

- **Multiple Input Formats**: Manual entry, TXT, CSV, Shapefile (.shp), GeoJSON
- **Flexible Coordinate Systems**: WGS84, UTM zones, custom projections
- **Automatic Tile Calculation**: Optimal zoom level and tile selection
- **Multi-Threaded Downloads**: Fast, concurrent tile downloading with caching
- **Seamless Mosaicking**: Automatic tile merging with no visible seams
- **Polygon Clipping**: Precise boundary extraction
- **ArcGIS Compatibility**: Full compatibility with ArcMap 10.8 and ArcGIS Pro
- **Professional Export**: GeoTIFF with embedded CRS, compression, and overviews
- **Batch Processing**: Process multiple polygons in queue
- **Modern UI**: Professional dark/light themes

## 🎯 Use Cases

- Cadastral mapping and land surveying
- Environmental monitoring and analysis
- Urban planning and development
- Agricultural field analysis
- Infrastructure project planning
- Research and education

## 📦 Installation

### Prerequisites

- **Operating System**: Windows 10/11 (64-bit)
- **Python**: 3.12 or higher
- **Disk Space**: 500 MB minimum (plus cache storage)

### Step 1: Install Python

Download and install Python 3.12 from [python.org](https://www.python.org/downloads/)

**Important**: During installation, check "Add Python to PATH"

### Step 2: Install GDAL

GDAL is required for geospatial operations. Install using one of these methods:

#### Option A: Using OSGeo4W (Recommended for Windows)

1. Download OSGeo4W installer from [trac.osgeo.org](https://trac.osgeo.org/osgeo4w/)
2. Run installer and select "Express Install"
3. Select GDAL and QGIS packages
4. Complete installation

#### Option B: Using Conda

```bash
conda install -c conda-forge gdal
```

### Step 3: Install Application

1. Download or clone the repository:
```bash
git clone https://github.com/your-repo/GeoTIFF-Satellite-Mosaic-Creator.git
cd GeoTIFF-Satellite-Mosaic-Creator
```

2. Create virtual environment (recommended):
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Step 4: Run Application

```bash
python -m app.main
```

## 🚀 Quick Start Guide

### 1. Input Coordinates

**Option A: Manual Entry**
1. Go to "Coordinates" tab
2. Click "Manual Entry"
3. Enter coordinates (one per line):
   ```
   -73.9857, 40.7484
   -73.9667, 40.7831
   -73.9492, 40.7589
   -73.9857, 40.7484
   ```
4. Click "Parse Coordinates"

**Option B: Import File**
- Click "Import TXT/CSV/SHP/GeoJSON"
- Select your file
- Configure column names (for CSV)

### 2. Create Polygon

1. Go to "Polygon" tab
2. Click "Create Polygon"
3. Review validation results
4. Click "Auto-Fix Issues" if needed

### 3. Configure Imagery

1. Go to "Imagery" tab
2. Select imagery provider (OpenStreetMap, Esri World Imagery, etc.)
3. Set zoom level (higher = more detail)

### 4. Set Export Options

1. Go to "Export" tab
2. Choose output format (GeoTIFF recommended)
3. Select output file path
4. Configure options:
   - ☑ Clip to polygon boundary
   - ☑ Build internal overviews

### 5. Generate Mosaic

1. Click "Start" button in toolbar
2. Monitor progress in Download panel
3. View logs in Log Console
4. Wait for completion message

### 6. Open in ArcGIS

1. Open ArcMap 10.8 or ArcGIS Pro
2. Add Data → select generated GeoTIFF
3. File automatically displays with correct georeferencing

## 📖 User Manual

### Coordinate Input Formats

**TXT Format:**
```
-73.9857, 40.7484
-73.9667, 40.7831
-73.9492, 40.7589
```

**CSV Format:**
```csv
x,y
-73.9857,40.7484
-73.9667,40.7831
-73.9492,40.7589
```

**Shapefile:**
- Must contain at least one polygon feature
- Automatically detects CRS
- Extracts exterior ring of first polygon

**GeoJSON:**
```json
{
  "type": "Feature",
  "geometry": {
    "type": "Polygon",
    "coordinates": [[
      [-73.9857, 40.7484],
      [-73.9667, 40.7831],
      [-73.9492, 40.7589],
      [-73.9857, 40.7484]
    ]]
  }
}
```

### Coordinate Systems

**Supported CRS:**
- EPSG:4326 (WGS84) - Geographic coordinates
- EPSG:3857 (Web Mercator) - Web mapping
- EPSG:32632 (UTM Zone 32N)
- EPSG:32633 (UTM Zone 33N)
- Custom EPSG codes

### Imagery Providers

**Built-in Providers:**
- **OpenStreetMap**: Free, global coverage, good for reference
- **Esri World Imagery**: High-resolution satellite imagery
- **CartoDB Positron**: Light base map

**Custom Providers:**
Add custom XYZ, WMTS, WMS, or ArcGIS tile services in configuration.

### Zoom Levels

- **10-12**: Regional scale (low detail, fast)
- **13-15**: Local scale (moderate detail)
- **16-18**: High detail (recommended for most uses)
- **19**: Maximum detail (very large files)

**Trade-off**: Higher zoom = better quality but more tiles and longer downloads

### Output Formats

- **GeoTIFF (.tif)**: Recommended - full ArcGIS compatibility
- **JPEG2000 (.jp2)**: Smaller files, good compression
- **PNG (.png)**: Lossless, larger files
- **JPEG (.jpg)**: Smallest files, lossy compression

### Batch Processing

1. Create multiple projects
2. Add to batch queue
3. Process all at once
4. Review results individually

## ⚙️ Configuration

Configuration file: `~/.geotiff_mosaic/config.json`

### Add Custom Imagery Provider

```json
{
  "imagery_providers": {
    "My Custom Provider": {
      "name": "My Custom Provider",
      "type": "xyz",
      "url": "https://example.com/{z}/{x}/{y}.png",
      "max_zoom": 19,
      "attribution": "© Custom Provider"
    }
  }
}
```

### Adjust Performance

```json
{
  "max_concurrent_downloads": 10,
  "download_timeout": 30,
  "max_retries": 3,
  "tile_size": 256
}
```

## 🔧 Troubleshooting

### Issue: GDAL Not Found

**Solution**: Ensure GDAL is properly installed and in PATH
```bash
python -c "from osgeo import gdal; print(gdal.__version__)"
```

### Issue: Download Errors

**Solution**: 
- Check internet connection
- Verify imagery provider URL
- Try lower zoom level
- Check firewall settings

### Issue: Output File Not Georeferenced

**Solution**:
- Ensure polygon has valid CRS
- Check polygon validation passed
- Verify no errors in log console

### Issue: Memory Errors

**Solution**:
- Reduce zoom level
- Process smaller polygon areas
- Close other applications
- Increase system RAM

### Issue: Slow Performance

**Solution**:
- Reduce max_concurrent_downloads
- Use lower zoom level
- Clear tile cache: `~/.geotiff_mosaic/cache/`
- Check disk space

## 📊 Performance Notes

**Typical Processing Times** (on modern PC):
- Small area (10 km²) at zoom 16: 2-5 minutes
- Medium area (50 km²) at zoom 16: 10-20 minutes
- Large area (100 km²) at zoom 16: 30-60 minutes

**Disk Usage**:
- Cache: ~30 KB per tile
- Output: Varies by compression (typically 10-100 MB)

## 🏗️ Architecture

```
app/
├── main.py                 # Application entry point
├── core/                   # Domain models and config
│   ├── models.py
│   └── config.py
├── services/              # Business logic
│   ├── coordinate_manager.py
│   ├── polygon_engine.py
│   ├── tile_calculator.py
│   ├── imagery_provider.py
│   ├── tile_downloader.py
│   ├── mosaic_builder.py
│   ├── raster_processor.py
│   ├── geotiff_exporter.py
│   ├── project_manager.py
│   └── workflow_orchestrator.py
├── gui/                   # User interface
│   ├── main_window.py
│   ├── styles.py
│   └── widgets/
└── utils/                 # Utilities
    ├── logger.py
    └── validators.py
```

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 👥 Authors

GeoTIFF Mosaic Creator Team

## 🙏 Acknowledgments

- OpenStreetMap contributors
- Esri for World Imagery
- GDAL/OGR community
- Rasterio developers
- PyQt6 team

## 📞 Support

For issues and questions:
- GitHub Issues: [Create an issue](https://github.com/your-repo/issues)
- Email: support@example.com
- Documentation: [Wiki](https://github.com/your-repo/wiki)

## 🗺️ Roadmap

Future enhancements:
- [ ] Interactive map preview with folium
- [ ] More imagery providers (Sentinel, Landsat)
- [ ] Temporal analysis (time series)
- [ ] Cloud processing integration
- [ ] Mobile app version
- [ ] Web-based interface

---

**Made with ❤️ for the GIS community**
