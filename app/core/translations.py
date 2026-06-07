"""
Translation system for multi-language support.
O'zbek va Ingliz tillari uchun tarjima tizimi.
"""
from typing import Dict, Any
import json
from pathlib import Path


class Translator:
    """Translation manager for application."""
    
    def __init__(self, language: str = "uz"):
        """
        Initialize translator.
        
        Args:
            language: Language code ("uz" or "en")
        """
        self.language = language
        self.translations = self._load_translations()
    
    def _load_translations(self) -> Dict[str, Any]:
        """Load translation dictionary."""
        translations = {
            "uz": UZ_TRANSLATIONS,
            "en": EN_TRANSLATIONS
        }
        return translations.get(self.language, UZ_TRANSLATIONS)
    
    def t(self, key: str) -> str:
        """
        Get translation for key.
        
        Args:
            key: Translation key (e.g., "menu.file.new")
            
        Returns:
            Translated string
        """
        keys = key.split('.')
        value = self.translations
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, key)
            else:
                return key
        
        return value if isinstance(value, str) else key
    
    def set_language(self, language: str):
        """Change language."""
        self.language = language
        self.translations = self._load_translations()


# O'ZBEK TILI TARJIMALARI
UZ_TRANSLATIONS = {
    "app": {
        "title": "GeoTIFF Sun'iy Yo'ldosh Mozaika Yaratuvchi",
        "ready": "Tayyor",
        "processing": "Ishlanmoqda...",
        "completed": "Bajarildi",
        "failed": "Xatolik",
        "cancelled": "Bekor qilindi"
    },
    
    "menu": {
        "file": {
            "title": "Fayl",
            "new": "Yangi Loyiha",
            "open": "Loyihani Ochish...",
            "save": "Saqlash",
            "save_as": "Boshqa Nom Bilan Saqlash...",
            "exit": "Chiqish"
        },
        "edit": {
            "title": "Tahrirlash",
            "settings": "Sozlamalar..."
        },
        "view": {
            "title": "Ko'rinish",
            "dark_theme": "Qorong'i Mavzu",
            "light_theme": "Yorug' Mavzu"
        },
        "help": {
            "title": "Yordam",
            "about": "Dastur Haqida",
            "user_guide": "Foydalanuvchi Qo'llanmasi"
        }
    },
    
    "toolbar": {
        "new": "Yangi",
        "open": "Ochish",
        "save": "Saqlash",
        "start": "Boshlash",
        "stop": "To'xtatish"
    },
    
    "tabs": {
        "coordinates": "Koordinatalar",
        "polygon": "Ko'pburchak",
        "imagery": "Sun'iy Yo'ldosh Tasvirlari",
        "download": "Yuklab Olish",
        "export": "Eksport"
    },
    
    "coordinate_panel": {
        "title": "Koordinatalar Kiritish",
        "input_method": "Kiritish Usuli",
        "manual_entry": "Qo'lda Kiritish",
        "import_txt": "TXT Fayldan Import",
        "import_csv": "CSV Fayldan Import",
        "import_shapefile": "Shapefile'dan Import",
        "import_geojson": "GeoJSON'dan Import",
        "crs_title": "Koordinata Tizimi",
        "crs_label": "Koordinata Tizimi:",
        "manual_group": "Qo'lda Kiritish",
        "manual_hint": "Koordinatalarni kiriting (har bir qatorda: x,y yoki lon,lat):",
        "manual_example": "Misol:\n-73.9857, 40.7484\n-73.9667, 40.7831\n...",
        "parse_btn": "Koordinatalarni Tahlil Qilish",
        "coordinates_table": "Koordinatalar",
        "col_number": "№",
        "col_x": "X / Uzunlik",
        "col_y": "Y / Kenglik",
        "clear_btn": "Tozalash",
        "apply_btn": "Ko'pburchakka Qo'llash",
        "warning": "Ogohlantirish",
        "enter_coordinates": "Iltimos, koordinatalar kiriting",
        "parse_errors": "Tahlil Xatoliklari",
        "success": "Muvaffaqiyat",
        "parsed_count": "{count} ta koordinata tahlil qilindi",
        "imported_count": "{count} ta koordinata import qilindi",
        "import_errors": "Import Xatoliklari"
    },
    
    "polygon_panel": {
        "title": "Ko'pburchak",
        "info_title": "Ko'pburchak Ma'lumotlari",
        "no_polygon": "Ko'pburchak yaratilmagan",
        "actions_title": "Amallar",
        "create_btn": "Ko'pburchak Yaratish",
        "validate_btn": "Ko'pburchakni Tekshirish",
        "fix_btn": "Avtomatik Tuzatish",
        "validation_title": "Tekshirish Natijalari",
        "insufficient_coords": "Yetarli Koordinatalar Yo'q",
        "min_3_coords": "Ko'pburchak yaratish uchun kamida 3 ta koordinata kerak",
        "error": "Xatolik",
        "create_failed": "Ko'pburchak yaratishda xatolik: {error}",
        "polygon_created": "Ko'pburchak {count} ta uchi bilan yaratildi",
        "valid": "✓ Ko'pburchak to'g'ri!",
        "invalid": "✗ Ko'pburchak tekshiruvdan o'tmadi:",
        "vertices": "Uchlar",
        "bounding_box": "Chegara Qutisi",
        "area": "Maydoni",
        "centroid": "Markaz",
        "square_degrees": "kvadrat daraja",
        "fix_success": "Ko'pburchak muammolari avtomatik tuzatildi!",
        "fix_failed": "Ko'pburchakni tuzatishda xatolik"
    },
    
    "imagery_panel": {
        "title": "Sun'iy Yo'ldosh Tasvirlari",
        "provider_title": "Tasvir Manbai",
        "select_provider": "Tasvir manbaini tanlang:",
        "zoom_title": "Kattalashtirish Darajasi",
        "zoom_label": "Kattalashtirish:",
        "zoom_hint": "(Yuqori = ko'proq tafsilot, ko'proq fayllar)"
    },
    
    "download_panel": {
        "title": "Yuklab Olish",
        "progress_title": "Yuklab Olish Jarayoni",
        "ready": "Tayyor",
        "downloading": "Yuklanmoqda: {current}/{total} plitkalar ({percent}%)",
        "stats_title": "Statistika",
        "no_downloads": "Hali yuklab olinmagan"
    },
    
    "export_panel": {
        "title": "Eksport",
        "format_title": "Chiqish Formati",
        "format_label": "Format:",
        "path_title": "Chiqish Yo'li",
        "path_placeholder": "Chiqish faylini tanlang...",
        "browse_btn": "Ko'rish...",
        "options_title": "Parametrlar",
        "clip_to_polygon": "Ko'pburchak chegarasigacha kesish",
        "export_full_extent": "To'liq chegarani ham eksport qilish",
        "build_overviews": "Ichki ko'rinishlarni yaratish",
        "save_output": "Chiqish Faylini Saqlash"
    },
    
    "map_preview": {
        "title": "Xarita Ko'rinishi",
        "placeholder": "Xarita ko'rinishi bu yerda paydo bo'ladi",
        "no_polygon": "Ko'pburchak yuklanmagan",
        "polygon_info": "Ko'pburchak: {vertices} uchlar",
        "valid": "✓ To'g'ri",
        "invalid": "✗ Noto'g'ri",
        "draw_instructions": "Xaritada ko'pburchak chizish uchun chizish vositalarini ishlating",
        "edit_instructions": "Ko'pburchakni tahrirlash uchun tanlang va tortib o'zgartiring"
    },
    
    "log_console": {
        "title": "Jurnal Konsoli"
    },
    
    "messages": {
        "new_project": "Yangi Loyiha",
        "current_project_close": "Joriy loyiha yopiladi. Davom ettirilsinmi?",
        "yes": "Ha",
        "no": "Yo'q",
        "new_project_created": "Yangi loyiha yaratildi",
        "project_opened": "Loyiha ochildi: {path}",
        "project_saved": "Loyiha saqlandi",
        "open_project": "Loyihani Ochish",
        "project_files": "Loyiha Fayllari (*.gmproj);;Barcha Fayllar (*.*)",
        "save_project_as": "Loyihani Saqlash",
        "exit_save": "Chiqish",
        "save_before_exit": "Chiqishdan oldin joriy loyihani saqlaysizmi?",
        "cancel": "Bekor qilish",
        "processing_started": "Ishlov berish boshlandi...",
        "processing_stopped": "Ishlov berish to'xtatildi",
        "theme_changed": "Mavzu {theme}ga o'zgartirildi",
        "settings": "Sozlamalar",
        "settings_not_implemented": "Sozlamalar dialogi hali amalga oshirilmagan",
        "about": "GeoTIFF Mozaika Yaratuvchi Haqida",
        "user_guide": "Foydalanuvchi Qo'llanmasi",
        "guide_not_implemented": "Foydalanuvchi qo'llanmasi hali amalga oshirilmagan"
    },
    
    "workflow": {
        "validating": "Ko'pburchak tekshirilmoqda...",
        "calculating": "Kerakli plitkalar hisoblanmoqda...",
        "downloading": "Plitkalar yuklab olinmoqda...",
        "mosaicking": "Mozaika qurilmoqda...",
        "clipping": "Ko'pburchakka kesib olinmoqda...",
        "exporting": "GeoTIFF eksport qilinmoqda...",
        "completed": "Ish jarayoni muvaffaqiyatli yakunlandi!",
        "failed": "Ish jarayonida xatolik: {error}"
    },
    
    "errors": {
        "failed_to_open": "Faylni ochishda xatolik: {error}",
        "failed_to_save": "Faylni saqlashda xatolik: {error}",
        "polygon_validation_failed": "Ko'pburchak tekshiruvidan o'tmadi",
        "no_coordinates": "Koordinatalar yo'q",
        "invalid_polygon": "Noto'g'ri ko'pburchak",
        "download_error": "Yuklab olishda xatolik",
        "export_error": "Eksport qilishda xatolik"
    }
}

# ENGLISH TRANSLATIONS
EN_TRANSLATIONS = {
    "app": {
        "title": "GeoTIFF Satellite Mosaic Creator",
        "ready": "Ready",
        "processing": "Processing...",
        "completed": "Completed",
        "failed": "Failed",
        "cancelled": "Cancelled"
    },
    
    "menu": {
        "file": {
            "title": "File",
            "new": "New Project",
            "open": "Open Project...",
            "save": "Save",
            "save_as": "Save As...",
            "exit": "Exit"
        },
        "edit": {
            "title": "Edit",
            "settings": "Settings..."
        },
        "view": {
            "title": "View",
            "dark_theme": "Dark Theme",
            "light_theme": "Light Theme"
        },
        "help": {
            "title": "Help",
            "about": "About",
            "user_guide": "User Guide"
        }
    },
    
    "toolbar": {
        "new": "New",
        "open": "Open",
        "save": "Save",
        "start": "Start",
        "stop": "Stop"
    },
    
    "tabs": {
        "coordinates": "Coordinates",
        "polygon": "Polygon",
        "imagery": "Imagery",
        "download": "Download",
        "export": "Export"
    },
    
    # ... rest of English translations
}


# Global translator instance
_translator = Translator("uz")


def get_translator() -> Translator:
    """Get global translator instance."""
    return _translator


def t(key: str) -> str:
    """Shortcut function for translation."""
    return _translator.t(key)


def set_language(language: str):
    """Change application language."""
    _translator.set_language(language)
