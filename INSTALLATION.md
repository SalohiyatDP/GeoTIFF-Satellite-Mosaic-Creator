# Installation Guide

## Windows Installation

### Prerequisites

1. **Windows 10/11** (64-bit)
2. **Python 3.12+** from [python.org](https://www.python.org/downloads/)
3. **GDAL** (geospatial library)

### Method 1: Development Installation (Recommended for Developers)

#### Step 1: Install Python

1. Download Python 3.12 installer
2. Run installer
3. ☑ Check "Add Python to PATH"
4. Click "Install Now"

#### Step 2: Install GDAL

**Option A: OSGeo4W (Easiest)**

1. Download [OSGeo4W installer](https://trac.osgeo.org/osgeo4w/)
2. Run installer
3. Select "Express Install"
4. Select GDAL package
5. Complete installation
6. Add to system PATH:
   ```
   C:\OSGeo4W64\bin
   ```

**Option B: Conda**

```bash
conda create -n geotiff python=3.12
conda activate geotiff
conda install -c conda-forge gdal
```

#### Step 3: Clone Repository

```bash
git clone https://github.com/your-repo/GeoTIFF-Satellite-Mosaic-Creator.git
cd GeoTIFF-Satellite-Mosaic-Creator
```

#### Step 4: Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

#### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

#### Step 6: Verify Installation

```bash
python -c "from osgeo import gdal; print('GDAL version:', gdal.__version__)"
python -c "import rasterio; print('Rasterio OK')"
python -c "from PyQt6.QtWidgets import QApplication; print('PyQt6 OK')"
```

#### Step 7: Run Application

```bash
python -m app.main
```

### Method 2: Standalone Executable (Recommended for End Users)

#### Option A: Download Pre-built Executable

1. Download latest release from [Releases](https://github.com/your-repo/releases)
2. Extract ZIP file
3. Run `GeoTIFF_Mosaic_Creator.exe`

#### Option B: Build Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller geotiff_mosaic.spec

# Find executable in:
dist/GeoTIFF_Mosaic_Creator/GeoTIFF_Mosaic_Creator.exe
```

### Method 3: Create Windows Installer

#### Using Inno Setup

1. Install [Inno Setup](https://jrsoftware.org/isinfo.php)
2. Create installer script (`installer.iss`):

```iss
[Setup]
AppName=GeoTIFF Mosaic Creator
AppVersion=1.0.0
DefaultDirName={pf}\GeoTIFF Mosaic Creator
DefaultGroupName=GeoTIFF Mosaic Creator
OutputDir=installer
OutputBaseFilename=GeoTIFF_Mosaic_Creator_Setup

[Files]
Source: "dist\GeoTIFF_Mosaic_Creator\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\GeoTIFF Mosaic Creator"; Filename: "{app}\GeoTIFF_Mosaic_Creator.exe"
Name: "{commondesktop}\GeoTIFF Mosaic Creator"; Filename: "{app}\GeoTIFF_Mosaic_Creator.exe"
```

3. Compile with Inno Setup
4. Installer created in `installer/` directory

## Linux Installation

### Ubuntu/Debian

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install python3.12 python3-pip python3-venv
sudo apt-get install gdal-bin libgdal-dev
sudo apt-get install python3-pyqt6

# Clone repository
git clone https://github.com/your-repo/GeoTIFF-Satellite-Mosaic-Creator.git
cd GeoTIFF-Satellite-Mosaic-Creator

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python -m app.main
```

### Fedora/CentOS/RHEL

```bash
# Install system dependencies
sudo dnf install python3.12 python3-pip
sudo dnf install gdal gdal-devel
sudo dnf install python3-qt6

# Follow same steps as Ubuntu
```

## macOS Installation

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python@3.12
brew install gdal
brew install pyqt6

# Clone repository
git clone https://github.com/your-repo/GeoTIFF-Satellite-Mosaic-Creator.git
cd GeoTIFF-Satellite-Mosaic-Creator

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python -m app.main
```

## Docker Installation (Advanced)

```dockerfile
FROM python:3.12-slim

# Install GDAL
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    python3-pyqt6 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy application
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run application
CMD ["python", "-m", "app.main"]
```

Build and run:
```bash
docker build -t geotiff-mosaic .
docker run -it geotiff-mosaic
```

## Troubleshooting Installation

### Issue: GDAL Import Error

**Error**: `ImportError: No module named 'osgeo'`

**Solutions**:
1. Check GDAL installation: `gdalinfo --version`
2. Install GDAL Python bindings: `pip install GDAL==$(gdal-config --version)`
3. Set environment variables:
   ```bash
   set GDAL_DATA=C:\OSGeo4W64\share\gdal
   set PROJ_LIB=C:\OSGeo4W64\share\proj
   ```

### Issue: PyQt6 Not Found

**Error**: `ModuleNotFoundError: No module named 'PyQt6'`

**Solution**:
```bash
pip install PyQt6
```

### Issue: Rasterio Build Error

**Error**: Build errors during `pip install rasterio`

**Solution**:
```bash
# Use pre-built wheels
pip install rasterio --find-links=https://www.lfd.uci.edu/~gohlke/pythonlibs/
```

### Issue: Permission Denied

**Error**: `Permission denied` during installation

**Solution**:
- Windows: Run Command Prompt as Administrator
- Linux/Mac: Use `sudo` for system packages

### Issue: Version Conflicts

**Error**: Dependency version conflicts

**Solution**:
```bash
# Create fresh virtual environment
python -m venv venv_new
source venv_new/bin/activate  # or venv_new\Scripts\activate on Windows
pip install -r requirements.txt
```

## Verification

After installation, verify all components:

```python
python -c "
import sys
print('Python:', sys.version)

from osgeo import gdal
print('GDAL:', gdal.__version__)

import rasterio
print('Rasterio:', rasterio.__version__)

from PyQt6.QtWidgets import QApplication
print('PyQt6: OK')

import geopandas
print('GeoPandas:', geopandas.__version__)

import shapely
print('Shapely:', shapely.__version__)

print('\nAll components installed successfully!')
"
```

## Updating

```bash
# Update from git
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade
```

## Uninstallation

### Development Installation

```bash
# Deactivate virtual environment
deactivate

# Remove directory
rm -rf GeoTIFF-Satellite-Mosaic-Creator  # Linux/Mac
rmdir /s GeoTIFF-Satellite-Mosaic-Creator  # Windows
```

### Standalone Installation

- Windows: Use "Add or Remove Programs"
- Delete application directory manually

## Support

For installation issues:
- Check [Troubleshooting](README.md#troubleshooting) section
- Create [GitHub Issue](https://github.com/your-repo/issues)
- Email: support@example.com
