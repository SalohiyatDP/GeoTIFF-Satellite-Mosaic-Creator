# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for GeoTIFF Satellite Mosaic Creator
Usage: pyinstaller geotiff_mosaic.spec
"""

import sys
from pathlib import Path

block_cipher = None

# Application paths
app_path = Path('app')
icon_path = 'app/resources/icon.ico' if Path('app/resources/icon.ico').exists() else None

# Collect all Python files
app_files = []
for py_file in app_path.rglob('*.py'):
    app_files.append((str(py_file), str(py_file.parent)))

# GDAL data files (required for coordinate transformations)
gdal_data_files = []
try:
    from osgeo import gdal
    gdal_data = Path(gdal.GetConfigOption('GDAL_DATA'))
    if gdal_data.exists():
        gdal_data_files = [(str(gdal_data), 'gdal-data')]
except:
    pass

# Analysis
a = Analysis(
    ['app/main.py'],
    pathex=[],
    binaries=[],
    datas=app_files + gdal_data_files,
    hiddenimports=[
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'rasterio',
        'rasterio.mask',
        'rasterio.merge',
        'rasterio.warp',
        'rasterio.features',
        'rasterio.shutil',
        'osgeo',
        'osgeo.gdal',
        'osgeo.osr',
        'osgeo.ogr',
        'geopandas',
        'shapely',
        'shapely.geometry',
        'fiona',
        'pyproj',
        'mercantile',
        'requests',
        'numpy',
        'pandas',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'IPython',
        'jupyter',
        'notebook',
        'PIL',
        'tkinter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# PYZ
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# EXE
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='GeoTIFF_Mosaic_Creator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path,
)

# COLLECT
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='GeoTIFF_Mosaic_Creator',
)
