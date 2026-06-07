"""
GUI styles and themes.
"""

DARK_THEME = """
QMainWindow {
    background-color: #2b2b2b;
}

QWidget {
    background-color: #2b2b2b;
    color: #d4d4d4;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 10pt;
}

QPushButton {
    background-color: #0e639c;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #1177bb;
}

QPushButton:pressed {
    background-color: #0d5689;
}

QPushButton:disabled {
    background-color: #3c3c3c;
    color: #808080;
}

QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox {
    background-color: #3c3c3c;
    border: 1px solid #555555;
    border-radius: 3px;
    padding: 5px;
    color: #d4d4d4;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #0e639c;
}

QComboBox {
    background-color: #3c3c3c;
    border: 1px solid #555555;
    border-radius: 3px;
    padding: 5px;
    color: #d4d4d4;
}

QComboBox:hover {
    border: 1px solid #0e639c;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #d4d4d4;
    margin-right: 5px;
}

QTableWidget {
    background-color: #2b2b2b;
    alternate-background-color: #3c3c3c;
    gridline-color: #555555;
    border: 1px solid #555555;
}

QTableWidget::item {
    padding: 5px;
}

QTableWidget::item:selected {
    background-color: #0e639c;
}

QHeaderView::section {
    background-color: #3c3c3c;
    color: #d4d4d4;
    padding: 5px;
    border: 1px solid #555555;
    font-weight: bold;
}

QTabWidget::pane {
    border: 1px solid #555555;
    background-color: #2b2b2b;
}

QTabBar::tab {
    background-color: #3c3c3c;
    color: #d4d4d4;
    padding: 8px 16px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}

QTabBar::tab:selected {
    background-color: #0e639c;
    color: white;
}

QTabBar::tab:hover {
    background-color: #4c4c4c;
}

QGroupBox {
    border: 1px solid #555555;
    border-radius: 5px;
    margin-top: 10px;
    padding-top: 10px;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}

QProgressBar {
    border: 1px solid #555555;
    border-radius: 3px;
    background-color: #3c3c3c;
    text-align: center;
    color: white;
}

QProgressBar::chunk {
    background-color: #0e639c;
    border-radius: 2px;
}

QLabel {
    color: #d4d4d4;
}

QCheckBox {
    color: #d4d4d4;
    spacing: 5px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #555555;
    border-radius: 3px;
    background-color: #3c3c3c;
}

QCheckBox::indicator:checked {
    background-color: #0e639c;
    border-color: #0e639c;
}

QRadioButton {
    color: #d4d4d4;
    spacing: 5px;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #555555;
    border-radius: 9px;
    background-color: #3c3c3c;
}

QRadioButton::indicator:checked {
    background-color: #0e639c;
    border-color: #0e639c;
}

QScrollBar:vertical {
    background-color: #2b2b2b;
    width: 12px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #555555;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #666666;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #2b2b2b;
    height: 12px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background-color: #555555;
    border-radius: 6px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #666666;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

QMenuBar {
    background-color: #2b2b2b;
    color: #d4d4d4;
}

QMenuBar::item:selected {
    background-color: #0e639c;
}

QMenu {
    background-color: #2b2b2b;
    color: #d4d4d4;
    border: 1px solid #555555;
}

QMenu::item:selected {
    background-color: #0e639c;
}

QStatusBar {
    background-color: #2b2b2b;
    color: #d4d4d4;
}

QToolBar {
    background-color: #3c3c3c;
    border: none;
    spacing: 3px;
    padding: 3px;
}

QToolButton {
    background-color: transparent;
    border: none;
    padding: 5px;
    border-radius: 3px;
}

QToolButton:hover {
    background-color: #4c4c4c;
}

QToolButton:pressed {
    background-color: #0e639c;
}
"""

LIGHT_THEME = """
QMainWindow {
    background-color: #f0f0f0;
}

QWidget {
    background-color: #f0f0f0;
    color: #000000;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 10pt;
}

QPushButton {
    background-color: #0078d4;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #106ebe;
}

QPushButton:pressed {
    background-color: #005a9e;
}

QPushButton:disabled {
    background-color: #cccccc;
    color: #666666;
}

QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox {
    background-color: white;
    border: 1px solid #cccccc;
    border-radius: 3px;
    padding: 5px;
    color: #000000;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #0078d4;
}

QComboBox {
    background-color: white;
    border: 1px solid #cccccc;
    border-radius: 3px;
    padding: 5px;
    color: #000000;
}

QComboBox:hover {
    border: 1px solid #0078d4;
}

QTableWidget {
    background-color: white;
    alternate-background-color: #f5f5f5;
    gridline-color: #cccccc;
    border: 1px solid #cccccc;
}

QTableWidget::item:selected {
    background-color: #0078d4;
    color: white;
}

QHeaderView::section {
    background-color: #e0e0e0;
    color: #000000;
    padding: 5px;
    border: 1px solid #cccccc;
    font-weight: bold;
}

QTabWidget::pane {
    border: 1px solid #cccccc;
    background-color: #f0f0f0;
}

QTabBar::tab {
    background-color: #e0e0e0;
    color: #000000;
    padding: 8px 16px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}

QTabBar::tab:selected {
    background-color: #0078d4;
    color: white;
}

QTabBar::tab:hover {
    background-color: #d0d0d0;
}

QGroupBox {
    border: 1px solid #cccccc;
    border-radius: 5px;
    margin-top: 10px;
    padding-top: 10px;
    font-weight: bold;
}

QProgressBar {
    border: 1px solid #cccccc;
    border-radius: 3px;
    background-color: white;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #0078d4;
    border-radius: 2px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #cccccc;
    border-radius: 3px;
    background-color: white;
}

QCheckBox::indicator:checked {
    background-color: #0078d4;
    border-color: #0078d4;
}

QScrollBar:vertical {
    background-color: #f0f0f0;
    width: 12px;
}

QScrollBar::handle:vertical {
    background-color: #cccccc;
    border-radius: 6px;
}

QScrollBar::handle:vertical:hover {
    background-color: #b0b0b0;
}

QMenuBar {
    background-color: #f0f0f0;
    color: #000000;
}

QMenuBar::item:selected {
    background-color: #0078d4;
    color: white;
}

QMenu {
    background-color: white;
    color: #000000;
    border: 1px solid #cccccc;
}

QMenu::item:selected {
    background-color: #0078d4;
    color: white;
}
"""


def get_theme(theme_name: str = "dark") -> str:
    """
    Get theme stylesheet.
    
    Args:
        theme_name: Theme name ('dark' or 'light')
        
    Returns:
        Stylesheet string
    """
    if theme_name.lower() == "light":
        return LIGHT_THEME
    return DARK_THEME
