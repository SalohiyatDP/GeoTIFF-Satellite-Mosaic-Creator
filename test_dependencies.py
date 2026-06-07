"""
Test script to check all dependencies.
Barcha kutubxonalarni tekshirish uchun test skript.
"""
import sys

print("=" * 60)
print("KUTUBXONALARNI TEKSHIRISH")
print("=" * 60)

# Test 1: PyQt6
print("\n1. PyQt6 tekshirilmoqda...")
try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    print("   ✅ PyQt6 - O'RNATILGAN")
except ImportError as e:
    print(f"   ❌ PyQt6 - O'RNATILMAGAN: {e}")
    print("   📦 O'rnatish: pip install PyQt6")

# Test 2: PyQt6-WebEngine
print("\n2. PyQt6-WebEngine tekshirilmoqda...")
try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    print("   ✅ PyQt6-WebEngine - O'RNATILGAN")
except ImportError as e:
    print(f"   ❌ PyQt6-WebEngine - O'RNATILMAGAN: {e}")
    print("   📦 O'rnatish: pip install PyQt6-WebEngine")

# Test 3: Folium
print("\n3. Folium tekshirilmoqda...")
try:
    import folium
    from folium import plugins
    print(f"   ✅ Folium - O'RNATILGAN (versiya: {folium.__version__})")
except ImportError as e:
    print(f"   ❌ Folium - O'RNATILMAGAN: {e}")
    print("   📦 O'rnatish: pip install folium branca")

# Test 4: Branca
print("\n4. Branca tekshirilmoqda...")
try:
    import branca
    print(f"   ✅ Branca - O'RNATILGAN (versiya: {branca.__version__})")
except ImportError as e:
    print(f"   ❌ Branca - O'RNATILMAGAN: {e}")
    print("   📦 O'rnatish: pip install branca")

# Test 5: GDAL
print("\n5. GDAL tekshirilmoqda...")
try:
    from osgeo import gdal
    print(f"   ✅ GDAL - O'RNATILGAN (versiya: {gdal.__version__})")
except ImportError as e:
    print(f"   ❌ GDAL - O'RNATILMAGAN: {e}")
    print("   📦 O'rnatish: OSGeo4W yoki conda install -c conda-forge gdal")

# Test 6: Rasterio
print("\n6. Rasterio tekshirilmoqda...")
try:
    import rasterio
    print(f"   ✅ Rasterio - O'RNATILGAN (versiya: {rasterio.__version__})")
except ImportError as e:
    print(f"   ❌ Rasterio - O'RNATILMAGAN: {e}")
    print("   📦 O'rnatish: pip install rasterio")

# Test 7: GeoPandas
print("\n7. GeoPandas tekshirilmoqda...")
try:
    import geopandas
    print(f"   ✅ GeoPandas - O'RNATILGAN (versiya: {geopandas.__version__})")
except ImportError as e:
    print(f"   ❌ GeoPandas - O'RNATILMAGAN: {e}")
    print("   📦 O'rnatish: pip install geopandas")

# Test 8: Shapely
print("\n8. Shapely tekshirilmoqda...")
try:
    import shapely
    print(f"   ✅ Shapely - O'RNATILGAN (versiya: {shapely.__version__})")
except ImportError as e:
    print(f"   ❌ Shapely - O'RNATILMAGAN: {e}")
    print("   📦 O'rnatish: pip install shapely")

# Test 9: Mercantile
print("\n9. Mercantile tekshirilmoqda...")
try:
    import mercantile
    print(f"   ✅ Mercantile - O'RNATILGAN (versiya: {mercantile.__version__})")
except ImportError as e:
    print(f"   ❌ Mercantile - O'RNATILMAGAN: {e}")
    print("   📦 O'rnatish: pip install mercantile")

# Test 10: Requests
print("\n10. Requests tekshirilmoqda...")
try:
    import requests
    print(f"   ✅ Requests - O'RNATILGAN (versiya: {requests.__version__})")
except ImportError as e:
    print(f"   ❌ Requests - O'RNATILMAGAN: {e}")
    print("   📦 O'rnatish: pip install requests")

print("\n" + "=" * 60)
print("NATIJA")
print("=" * 60)

# Count installed
installed_count = 0
total_count = 10

dependencies = [
    ('PyQt6', 'PyQt6.QtWidgets'),
    ('PyQt6-WebEngine', 'PyQt6.QtWebEngineWidgets'),
    ('Folium', 'folium'),
    ('Branca', 'branca'),
    ('GDAL', 'osgeo'),
    ('Rasterio', 'rasterio'),
    ('GeoPandas', 'geopandas'),
    ('Shapely', 'shapely'),
    ('Mercantile', 'mercantile'),
    ('Requests', 'requests')
]

for name, module in dependencies:
    try:
        __import__(module)
        installed_count += 1
    except ImportError:
        pass

print(f"\n✅ O'rnatilgan: {installed_count}/{total_count}")
print(f"❌ O'rnatilmagan: {total_count - installed_count}/{total_count}")

if installed_count == total_count:
    print("\n🎉 AJOYIB! Barcha kutubxonalar o'rnatilgan!")
    print("✅ Dasturni ishga tushirishingiz mumkin: python -m app.main")
else:
    print("\n⚠️  DIQQAT! Ba'zi kutubxonalar o'rnatilmagan.")
    print("\n📦 BARCHA KUTUBXONALARNI O'RNATISH:")
    print("   pip install -r requirements.txt")
    print("\n🔥 XARITA UCHUN MUHIM:")
    print("   pip install folium branca PyQt6-WebEngine")

print("\n" + "=" * 60)
print("Python versiyasi:", sys.version)
print("=" * 60)
