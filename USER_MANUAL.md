# GeoTIFF Satellite Mosaic Creator - User Manual

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [User Interface Overview](#user-interface-overview)
4. [Step-by-Step Workflow](#step-by-step-workflow)
5. [Advanced Features](#advanced-features)
6. [Best Practices](#best-practices)
7. [FAQ](#faq)
8. [Appendix](#appendix)

---

## 1. Introduction

### What is GeoTIFF Mosaic Creator?

GeoTIFF Mosaic Creator is a desktop application that automatically generates high-resolution georeferenced satellite image mosaics for any polygon area. The output GeoTIFF files are fully compatible with ArcMap 10.8 and ArcGIS Pro, requiring no manual georeferencing.

### Who Should Use This Application?

- Cadastral surveyors
- GIS professionals
- Environmental scientists
- Urban planners
- Agricultural analysts
- Students and researchers

### System Requirements

- **OS**: Windows 10/11 (64-bit recommended)
- **RAM**: 8 GB minimum, 16 GB recommended
- **Disk**: 500 MB application + cache storage
- **Internet**: Stable connection for tile downloads
- **Display**: 1280x720 minimum, 1920x1080 recommended

---

## 2. Getting Started

### First Launch

1. Start the application
2. The main window will open with dark theme (default)
3. All panels are empty and ready for input

### Interface Layout

The application window is divided into:
- **Left Side**: Control panels (tabs)
- **Right Side**: Map preview (top) and log console (bottom)
- **Top**: Menu bar and toolbar
- **Bottom**: Status bar

---

## 3. User Interface Overview

### Menu Bar

#### File Menu
- **New Project** (Ctrl+N): Start a new project
- **Open Project** (Ctrl+O): Load existing project
- **Save Project** (Ctrl+S): Save current project
- **Save Project As** (Ctrl+Shift+S): Save with new name
- **Exit** (Alt+F4): Close application

#### Edit Menu
- **Settings**: Configure application preferences

#### View Menu
- **Dark Theme**: Apply dark color scheme
- **Light Theme**: Apply light color scheme

#### Help Menu
- **About**: Application information
- **User Guide**: Open this manual

### Toolbar

- **New**: Create new project
- **Open**: Load project file
- **Save**: Save current project
- **Start**: Begin mosaic generation
- **Stop**: Cancel ongoing process

### Status Bar

Shows current application status and messages

---

## 4. Step-by-Step Workflow

### Step 1: Input Coordinates

#### Method A: Manual Entry

1. Click **Coordinates** tab
2. Click **Manual Entry** button
3. Text area appears
4. Enter coordinates (one per line):
   ```
   longitude, latitude
   -73.9857, 40.7484
   -73.9667, 40.7831
   -73.9492, 40.7589
   -73.9857, 40.7484
   ```
5. Click **Parse Coordinates**
6. Review parsed coordinates in table
7. Click **Apply to Polygon**

**Tips:**
- Coordinates can be comma or space separated
- Lines starting with # are ignored (comments)
- First and last coordinates should match (polygon closure)

#### Method B: Import TXT File

1. Click **Import TXT** button
2. Select .txt file containing coordinates
3. File format: one coordinate pair per line
4. Coordinates automatically parsed
5. Review in table
6. Click **Apply to Polygon**

#### Method C: Import CSV File

1. Click **Import CSV** button
2. Select .csv file
3. Default columns: "x" and "y"
4. Custom columns can be specified in code
5. Review parsed data
6. Click **Apply to Polygon**

**CSV Example:**
```csv
x,y
-73.9857,40.7484
-73.9667,40.7831
-73.9492,40.7589
```

#### Method D: Import Shapefile

1. Click **Import Shapefile** button
2. Select .shp file
3. First polygon automatically extracted
4. CRS detected automatically
5. Coordinates displayed
6. Click **Apply to Polygon**

**Requirements:**
- Shapefile must contain polygon features
- .shx and .dbf files must be present
- Supported: Polygon and MultiPolygon

#### Method E: Import GeoJSON

1. Click **Import GeoJSON** button
2. Select .geojson or .json file
3. First feature extracted
4. Supports FeatureCollection, Feature, or Geometry
5. Coordinates displayed
6. Click **Apply to Polygon**

#### Coordinate System Selection

In the **Coordinate System** group:
1. Select appropriate CRS from dropdown
2. Options:
   - **EPSG:4326** (WGS84): Standard GPS coordinates
   - **EPSG:3857** (Web Mercator): Web mapping
   - **EPSG:32632** (UTM 32N): Europe
   - **EPSG:32633** (UTM 33N): Europe
3. Coordinates are interpreted in selected CRS

### Step 2: Create and Validate Polygon

1. Switch to **Polygon** tab
2. After applying coordinates, **Create Polygon** button becomes active
3. Click **Create Polygon**
4. Polygon is automatically:
   - Created from coordinates
   - Closed (if not already)
   - Validated for errors
5. Review **Validation Results**:
   - ✓ Green checkmark = Valid
   - ✗ Red X = Invalid with error list
6. Review **Polygon Information**:
   - Number of vertices
   - Bounding box
   - Area (square degrees)
   - Centroid coordinates

#### Validation Issues

Common validation errors:
- **Too few vertices**: Need at least 3 points
- **Self-intersections**: Polygon crosses itself
- **Zero area**: All points are collinear
- **Not closed**: First and last points don't match

#### Auto-Fix Polygon Issues

1. If validation fails, click **Auto-Fix Issues**
2. Application attempts to:
   - Fix self-intersections
   - Remove duplicate vertices
   - Correct topology
3. If successful, polygon is updated
4. Review updated validation results

### Step 3: Configure Imagery Source

1. Switch to **Imagery** tab
2. **Select Imagery Source**:
   - **OpenStreetMap**: Free, global, moderate resolution
   - **Esri World Imagery**: High-resolution satellite
   - **CartoDB Positron**: Light base map
3. **Set Zoom Level**:
   - Minimum: 1 (global)
   - Maximum: 19 (street level)
   - Recommended: 16-18 for most uses

**Zoom Level Guide:**
- **10-12**: Regional overview (states, provinces)
- **13-15**: City/district level
- **16-17**: Neighborhood/cadastral parcels
- **18-19**: Building/property detail

**Trade-offs:**
- Higher zoom = More detail but more tiles
- More tiles = Longer download time and larger files
- Lower zoom = Faster but less detail

### Step 4: Configure Export Settings

1. Switch to **Export** tab
2. **Select Output Format**:
   - **GeoTIFF** (recommended): Full ArcGIS compatibility
   - **TIFF**: Standard TIFF with georeferencing
   - **JPEG2000**: Compressed, smaller files
   - **PNG**: Lossless, larger files
   - **JPEG**: Smallest files, lossy compression
3. **Choose Output Path**:
   - Click **Browse...** button
   - Navigate to desired folder
   - Enter filename
   - Click Save
4. **Configure Options**:
   - ☑ **Clip to polygon boundary**: Recommended
     - Cuts raster exactly to polygon shape
     - Removes unnecessary background
   - ☐ **Also export full extent**: Optional
     - Keeps rectangular extent
     - Useful for alignment with other data
   - ☑ **Build internal overviews**: Recommended
     - Creates pyramids for fast display
     - Essential for large files in ArcGIS

### Step 5: Generate Mosaic

1. Review all settings
2. Ensure output path is set
3. Click **Start** button in toolbar
4. Monitor progress:
   - **Download** tab shows tile download progress
   - **Log Console** shows detailed operations
   - Status bar shows current operation
5. Process stages:
   - Validating polygon
   - Calculating tiles
   - Downloading tiles
   - Building mosaic
   - Clipping to polygon
   - Exporting GeoTIFF
6. Wait for completion message
7. Output file created at specified path

**Progress Indicators:**
- Progress bar: Overall completion (0-100%)
- Status label: Current tiles downloaded
- Details label: Current operation
- Log console: Detailed step-by-step log

#### If Process Fails

1. Check log console for error messages
2. Common issues:
   - Internet connection lost
   - Invalid polygon geometry
   - Insufficient disk space
   - Output path not writable
3. Fix issue and restart

### Step 6: Open in ArcGIS

#### ArcMap 10.8

1. Open ArcMap
2. Click **Add Data** button (or Ctrl+D)
3. Navigate to output file
4. Select .tif file
5. Click **Add**
6. Image appears fully georeferenced
7. No manual georeferencing needed

#### ArcGIS Pro

1. Open ArcGIS Pro
2. Create or open project
3. In **Map** tab, click **Add Data** → **Data**
4. Navigate to output file
5. Select .tif file
6. Click **OK**
7. Image appears in correct location

**Verification:**
- Image should appear in correct geographic location
- No "Unknown Spatial Reference" warning
- Zoom and pan work correctly
- Coordinates display correctly

---

## 5. Advanced Features

### Project Management

#### Saving Projects

1. Click **File** → **Save Project**
2. Enter filename (*.gmproj)
3. Project includes:
   - All coordinates
   - Polygon geometry
   - Settings
   - Output paths
4. Use for:
   - Resuming work later
   - Sharing configurations
   - Batch processing

#### Loading Projects

1. Click **File** → **Open Project**
2. Select .gmproj file
3. All settings restored
4. Ready to regenerate or modify

### Batch Processing

#### Creating Batch Queue

1. Create first project
2. Add to batch queue (via code)
3. Create second project
4. Add to batch queue
5. Process all projects sequentially

**Use Cases:**
- Multiple parcels
- Same settings, different areas
- Overnight processing

### Custom Imagery Providers

#### Adding Custom Provider

Edit configuration file: `~/.geotiff_mosaic/config.json`

```json
{
  "imagery_providers": {
    "My Satellite": {
      "name": "My Satellite",
      "type": "xyz",
      "url": "https://tiles.example.com/{z}/{x}/{y}.jpg",
      "max_zoom": 18,
      "attribution": "© My Satellite Provider",
      "headers": {
        "User-Agent": "GeoTIFF-Mosaic-Creator",
        "API-Key": "your_api_key_here"
      }
    }
  }
}
```

Supported types:
- **xyz**: Standard tile format
- **wmts**: Web Map Tile Service
- **wms**: Web Map Service
- **arcgis**: ArcGIS REST API

### Performance Tuning

#### Adjust Download Settings

Edit config file:

```json
{
  "max_concurrent_downloads": 10,
  "download_timeout": 30,
  "max_retries": 3
}
```

- Increase concurrent downloads for faster speed
- Reduce if connection is unstable
- Adjust timeout for slow connections

#### Cache Management

Cache location: `~/.geotiff_mosaic/cache/`

To clear cache:
1. Close application
2. Delete cache folder
3. Restart application

**When to Clear:**
- Free up disk space
- Fix corrupt tile issues
- Update to newer imagery

---

## 6. Best Practices

### Coordinate Input

✅ **Do:**
- Close polygons (first = last coordinate)
- Use consistent coordinate system
- Validate coordinates before processing
- Keep polygon simple (minimize vertices)

❌ **Don't:**
- Mix coordinate systems
- Create extremely complex polygons (>1000 vertices)
- Use self-intersecting polygons
- Forget to specify CRS

### Zoom Level Selection

✅ **Do:**
- Start with zoom 15-16 for testing
- Increase to 17-18 for final output
- Consider area size vs. detail needed
- Check estimated file size

❌ **Don't:**
- Always use maximum zoom (unnecessary detail)
- Use zoom <13 for small areas (too coarse)
- Exceed 100 km² area at zoom 18

### File Management

✅ **Do:**
- Use descriptive filenames
- Save projects before processing
- Export project summaries
- Backup important outputs

❌ **Don't:**
- Overwrite existing files without backup
- Use spaces in filenames
- Save to network drives (use local first)

### Error Handling

✅ **Do:**
- Read error messages carefully
- Check log console for details
- Verify all inputs before starting
- Test with small area first

❌ **Don't:**
- Ignore validation warnings
- Skip polygon validation
- Process while unsure of settings

---

## 7. FAQ

### General Questions

**Q: How long does processing take?**

A: Depends on area size and zoom level:
- Small (1 km²) at zoom 16: 1-2 minutes
- Medium (10 km²) at zoom 17: 10-20 minutes
- Large (100 km²) at zoom 18: 1-2 hours

**Q: How much disk space is needed?**

A: Varies by zoom and compression:
- Cache: ~30 KB per tile
- Output GeoTIFF: 10-200 MB typical
- Higher zoom = more space

**Q: Can I use offline?**

A: No, internet connection required for tile downloads. However, cached tiles can be reused.

**Q: Is imagery up-to-date?**

A: Depends on provider:
- OpenStreetMap: Updated frequently
- Esri World Imagery: Varies by region
- Check provider documentation

**Q: Can I use commercial imagery?**

A: Yes, if you have API access. Add as custom provider with authentication headers.

### Technical Questions

**Q: Why is polygon validation important?**

A: Invalid polygons can cause:
- Incorrect tile calculations
- Mosaic errors
- Corrupt output files
- Processing failures

**Q: What if my polygon crosses antimeridian?**

A: Split into two polygons on either side of ±180° longitude.

**Q: Can I process multiple polygons at once?**

A: Yes, use batch processing feature. Process each polygon as separate project.

**Q: How do I change coordinate systems?**

A: Use the CRS dropdown in Coordinates tab before importing/entering coordinates.

**Q: Why is my output file so large?**

A: Factors affecting file size:
- High zoom level
- Large area
- Lossless format (PNG, GeoTIFF)
- No compression

Solutions:
- Use JPEG2000 format
- Enable compression
- Reduce zoom level
- Clip to exact polygon

**Q: GeoTIFF won't open in ArcGIS?**

A: Check:
- File has .tif or .tiff extension
- File is not corrupted (>0 bytes)
- CRS is embedded (use validation)
- No processing errors in log

**Q: How to improve download speed?**

A: Options:
- Increase concurrent downloads (config)
- Use faster internet connection
- Choose closer tile server
- Process during off-peak hours

**Q: Can I pause and resume?**

A: Not directly. However:
- Cached tiles are reused
- Save project and restart

### Error Messages

**Q: "Failed to connect to tile server"**

A: Causes:
- No internet connection
- Firewall blocking access
- Server down
- Invalid provider URL

Solutions:
- Check internet connection
- Try different provider
- Check firewall settings
- Verify provider URL

**Q: "Polygon validation failed"**

A: Use Auto-Fix button or:
- Check for self-intersections
- Ensure >3 vertices
- Verify coordinates are correct
- Simplify complex polygon

**Q: "Out of memory"**

A: Solutions:
- Close other applications
- Reduce zoom level
- Process smaller area
- Increase system RAM
- Use 64-bit Python

**Q: "Permission denied writing file"**

A: Causes:
- File is open in another program
- No write permission
- Disk is full
- Network drive issues

Solutions:
- Close ArcGIS/other programs
- Choose different output folder
- Free up disk space
- Save to local drive first

---

## 8. Appendix

### A. Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+N | New Project |
| Ctrl+O | Open Project |
| Ctrl+S | Save Project |
| Ctrl+Shift+S | Save Project As |
| Alt+F4 | Exit Application |

### B. File Formats

#### Input Formats

| Format | Extension | Description |
|--------|-----------|-------------|
| Text | .txt | Plain text coordinates |
| CSV | .csv | Comma-separated values |
| Shapefile | .shp | ESRI Shapefile (with .shx, .dbf) |
| GeoJSON | .geojson, .json | JSON-based format |

#### Output Formats

| Format | Extension | Compression | Quality | ArcGIS Support |
|--------|-----------|-------------|---------|----------------|
| GeoTIFF | .tif | LZW | Lossless | Excellent |
| JPEG2000 | .jp2 | JPEG2000 | Good | Good |
| PNG | .png | Deflate | Lossless | Fair |
| JPEG | .jpg | JPEG | Lossy | Fair |

### C. Coordinate Systems

| EPSG Code | Name | Type | Use Case |
|-----------|------|------|----------|
| 4326 | WGS84 | Geographic | GPS, global data |
| 3857 | Web Mercator | Projected | Web mapping |
| 32632 | UTM Zone 32N | Projected | Europe (0-6°E) |
| 32633 | UTM Zone 33N | Projected | Europe (6-12°E) |

### D. Imagery Provider Details

| Provider | Type | Max Zoom | Resolution | Update Frequency |
|----------|------|----------|------------|------------------|
| OpenStreetMap | XYZ | 19 | Variable | Continuous |
| Esri World Imagery | XYZ | 19 | 0.3-1m | Quarterly |
| CartoDB Positron | XYZ | 19 | Vector | Real-time |

### E. Configuration File Structure

Location: `~/.geotiff_mosaic/config.json`

```json
{
  "cache_dir": "cache",
  "projects_dir": "projects",
  "logs_dir": "logs",
  "max_concurrent_downloads": 10,
  "download_timeout": 30,
  "max_retries": 3,
  "default_zoom_level": 18,
  "tile_size": 256,
  "compression_type": "LZW",
  "build_overviews": true,
  "theme": "dark",
  "map_preview_zoom": 12,
  "default_provider": "OpenStreetMap",
  "imagery_providers": {
    ...
  }
}
```

### F. Log File Location

Logs are saved to: `~/.geotiff_mosaic/logs/`

Format: `geotiff_mosaic_YYYYMMDD_HHMMSS.log`

### G. Glossary

- **Bounding Box**: Rectangular extent of polygon
- **CRS**: Coordinate Reference System
- **EPSG**: European Petroleum Survey Group (coordinate system codes)
- **GeoTIFF**: TIFF image with embedded geographic information
- **Mosaic**: Seamless image from multiple tiles
- **Overview**: Reduced-resolution copy for fast display
- **Tile**: Small image piece (typically 256×256 pixels)
- **UTM**: Universal Transverse Mercator projection
- **WGS84**: World Geodetic System 1984 (GPS standard)
- **Zoom Level**: Detail level (higher = more detail)

### H. Support Resources

- **GitHub Repository**: [Link]
- **Issues Tracker**: [Link]
- **Email Support**: support@example.com
- **Documentation**: [Wiki Link]
- **Video Tutorials**: [YouTube Channel]

---

**Document Version**: 1.0.0  
**Last Updated**: 2024  
**For Application Version**: 1.0.0

---

*This manual is subject to change. Check for updates regularly.*
