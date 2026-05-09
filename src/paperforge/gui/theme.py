"""Light Qt stylesheet inspired by the PaperForge color identity."""

from __future__ import annotations

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

PRIMARY = "#2E86AB"
SECONDARY = "#06A77D"
ACCENT = "#D62246"
NEUTRAL_BG = "#FAFBFC"
NEUTRAL_BORDER = "#D5DBE0"
TEXT = "#1F2933"
MUTED = "#52606D"

QSS = f"""
QWidget {{
    font-family: 'Segoe UI', 'Helvetica Neue', sans-serif;
    font-size: 10pt;
    color: {TEXT};
}}
QMainWindow, QDialog {{
    background-color: {NEUTRAL_BG};
}}
QTabWidget::pane {{
    border: 1px solid {NEUTRAL_BORDER};
    background: white;
    border-radius: 6px;
    top: -1px;
}}
QTabBar::tab {{
    padding: 8px 18px;
    background: transparent;
    border: 1px solid transparent;
    color: {MUTED};
}}
QTabBar::tab:selected {{
    color: {PRIMARY};
    border-bottom: 2px solid {PRIMARY};
    font-weight: 600;
}}
QPushButton {{
    background: white;
    border: 1px solid {NEUTRAL_BORDER};
    padding: 6px 14px;
    border-radius: 4px;
}}
QPushButton:hover {{
    border-color: {PRIMARY};
    color: {PRIMARY};
}}
QPushButton:pressed {{ background: #EDF3F7; }}
QPushButton:disabled {{ color: #99A; background: #F2F4F7; }}

QPushButton#PrimaryButton {{
    background: {PRIMARY};
    color: white;
    font-weight: 600;
    border: none;
    padding: 9px 20px;
    border-radius: 5px;
}}
QPushButton#PrimaryButton:hover {{ background: #226A8C; }}
QPushButton#PrimaryButton:pressed {{ background: #1A5572; }}
QPushButton#PrimaryButton:disabled {{ background: #B8C4CC; }}

QLineEdit, QPlainTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
    background: white;
    border: 1px solid {NEUTRAL_BORDER};
    padding: 4px 6px;
    border-radius: 3px;
    selection-background-color: {PRIMARY};
    selection-color: white;
}}
QLineEdit:focus, QPlainTextEdit:focus, QComboBox:focus,
QSpinBox:focus, QDoubleSpinBox:focus {{
    border: 1px solid {PRIMARY};
}}

QGroupBox {{
    border: 1px solid {NEUTRAL_BORDER};
    border-radius: 5px;
    margin-top: 14px;
    padding-top: 8px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 8px;
    padding: 0 4px;
    color: {PRIMARY};
    font-weight: 600;
}}

QStatusBar {{
    background: white;
    border-top: 1px solid {NEUTRAL_BORDER};
    color: {MUTED};
}}
QListWidget {{
    background: white;
    border: 1px solid {NEUTRAL_BORDER};
    border-radius: 4px;
}}
QListWidget::item:selected {{
    background: #E5F0F6;
    color: {PRIMARY};
}}
QHeaderView::section {{
    background: {PRIMARY};
    color: white;
    padding: 5px 8px;
    border: 0;
    font-weight: 600;
}}
QTableWidget {{
    background: white;
    gridline-color: {NEUTRAL_BORDER};
    border: 1px solid {NEUTRAL_BORDER};
}}
"""


def apply(app: QApplication) -> None:
    """Apply the global stylesheet + palette."""
    palette = app.palette()
    palette.setColor(QPalette.Window, QColor(NEUTRAL_BG))
    palette.setColor(QPalette.WindowText, QColor(TEXT))
    palette.setColor(QPalette.Base, QColor("white"))
    palette.setColor(QPalette.Highlight, QColor(PRIMARY))
    palette.setColor(QPalette.HighlightedText, QColor("white"))
    app.setPalette(palette)
    app.setStyleSheet(QSS)
