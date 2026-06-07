# ISHGA TUSHIRISH QO'LLANMASI

## ❌ XATOLIK: ModuleNotFoundError: No module named 'app'

### Sabab:
- Noto'g'ri papkada turibsiz
- Noto'g'ri buyruq ishlatilgan

### ✅ TO'G'RI YECHIM:

## 1-USUL: Module sifatida ishga tushirish (TAVSIYA ETILADI)

```bash
# Repository papkasiga kiring
cd D:\Projects\GeoTIFF-Satellite-Mosaic-Creator-main\app

# Bir papka yuqoriga chiqing (repository root'ga)
cd ..

# To'g'ri buyruq:
python -m app.main
```

## 2-USUL: To'g'ridan-to'g'ri app papkasidan

```bash
# app papkasiga kiring
cd D:\Projects\GeoTIFF-Satellite-Mosaic-Creator-main\app

# Ishga tushiring:
python main.py
```

## 3-USUL: To'liq yo'l ko'rsatish

```bash
# Repository root'da turing:
cd D:\Projects\GeoTIFF-Satellite-Mosaic-Creator-main

# Ishga tushiring:
python -m app.main
```

## BOSQICHMA-BOSQICH:

### 1. To'g'ri papkani tekshiring:

```powershell
# Qayerda ekanligingizni ko'ring:
pwd

# Chiqishi shunga o'xshash bo'lishi kerak:
# D:\Projects\GeoTIFF-Satellite-Mosaic-Creator-main
```

### 2. Fayl strukturasini tekshiring:

```powershell
# Fayllarni ko'ring:
dir

# Chiqishi:
# app (papka)
# README.md
# requirements.txt
# va boshqalar...
```

### 3. app papkasi ichidagi fayllarni tekshiring:

```powershell
dir app

# Chiqishi:
# main.py
# __init__.py
# core (papka)
# gui (papka)
# services (papka)
# utils (papka)
```

### 4. Agar hamma narsa to'g'ri bo'lsa:

```powershell
python -m app.main
```

## AGAR BARIBIR ISHLAMASA:

### A. Virtual environment yarating:

```powershell
# Repository root'da:
python -m venv venv

# Aktivlashtiring:
venv\Scripts\activate

# Dependencies o'rnating:
pip install -r requirements.txt

# Ishga tushiring:
python -m app.main
```

### B. Python yo'lini qo'shing:

```powershell
# PYTHONPATH ni sozlang:
$env:PYTHONPATH = "D:\Projects\GeoTIFF-Satellite-Mosaic-Creator-main"

# Ishga tushiring:
python -m app.main
```

### C. Dependencies tekshiring:

```powershell
# PyQt6 o'rnatilganini tekshiring:
python -c "import PyQt6; print('PyQt6 OK')"

# GDAL tekshirish:
python -c "from osgeo import gdal; print('GDAL OK')"

# Folium tekshirish:
python -c "import folium; print('Folium OK')"
```

## XATOLIKLARNI TUZATISH:

### Xatolik: Cannot find 'app' module

**Yechim:**
```powershell
# Repository root'ga o'ting:
cd D:\Projects\GeoTIFF-Satellite-Mosaic-Creator-main

# Bu buyruqni ishlating:
python -m app.main
```

### Xatolik: No module named 'PyQt6'

**Yechim:**
```powershell
pip install PyQt6 PyQt6-WebEngine
```

### Xatolik: No module named 'osgeo'

**Yechim:**
```powershell
# OSGeo4W o'rnating:
# https://trac.osgeo.org/osgeo4w/

# Yoki Conda ishlatib:
conda install -c conda-forge gdal
```

## TO'G'RI BUYRUQLAR KETMA-KETLIGI:

```powershell
# 1. Repository papkasiga o'ting
cd D:\Projects\GeoTIFF-Satellite-Mosaic-Creator-main

# 2. Qayerda ekanligingizni tekshiring
pwd
# Natija: D:\Projects\GeoTIFF-Satellite-Mosaic-Creator-main

# 3. app papkasi borligini tekshiring
dir app
# Natija: main.py, __init__.py, va boshqalar

# 4. Ishga tushiring
python -m app.main
```

## MUVAFFAQIYATLI ISHGA TUSHIRISH:

Agar hamma narsa to'g'ri bo'lsa, siz ko'rasiz:

```
✅ Dastur oynasi ochiladi
✅ "GeoTIFF Sun'iy Yo'ldosh Mozaika Yaratuvchi" sarlavhasi
✅ Xarita ko'rinadi (Toshkent markazida)
✅ 5 ta tab: Koordinatalar, Ko'pburchak, va h.k.
```

## YORDAM:

Agar hali ham ishlamasa:
1. Screenshot yuboring
2. Qaysi papkada turganingizni ko'rsating (pwd)
3. dir buyrug'i natijasini yuboring
4. Python versiyasini tekshiring: python --version

