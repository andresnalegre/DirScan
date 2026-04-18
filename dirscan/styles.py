BG       = "#111113"
SURFACE  = "#1c1c1e"
SURFACE2 = "#242426"
BORDER   = "#2c2c2e"
BORDER2  = "#3a3a3c"
ACCENT   = "#0a84ff"
ACCENT_H = "#0070d8"
GREEN    = "#30d158"
TEXT1    = "#f5f5f7"
TEXT2    = "#aeaeb2"
TEXT3    = "#636366"
TEXT4    = "#48484a"


def get_stylesheet() -> str:
    return f"""
        * {{
            font-family: -apple-system, "SF Pro Display", "Helvetica Neue", sans-serif;
        }}

        QMainWindow {{
            background-color: {BG};
        }}

        QWidget {{
            background-color: {BG};
            color: {TEXT1};
        }}

        #buttonContainer {{
            background-color: {SURFACE};
            border-bottom: 1px solid {BORDER};
            margin: 0px;
            padding: 0px;
        }}

        QPushButton {{
            background-color: {ACCENT};
            color: white;
            border: none;
            padding: 9px 22px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 500;
            min-width: 130px;
        }}

        QPushButton:hover {{
            background-color: {ACCENT_H};
        }}

        QPushButton:pressed {{
            background-color: #005bb5;
        }}

        QPushButton:disabled {{
            background-color: {BORDER};
            color: {TEXT4};
        }}

        QPushButton#saveButton {{
            background-color: {BORDER};
            color: {TEXT4};
        }}

        QPushButton#saveButton:enabled {{
            background-color: {GREEN};
            color: white;
        }}

        QPushButton#saveButton:enabled:hover {{
            background-color: #28b84c;
        }}

        QPushButton#saveButton:enabled:pressed {{
            background-color: #1e9e3e;
        }}

        QTextEdit {{
            background-color: {SURFACE};
            color: #e5e5ea;
            border: 1px solid {BORDER};
            border-radius: 10px;
            padding: 14px;
            font-family: "Menlo", "SF Mono", "Courier New", monospace;
            font-size: 12px;
            selection-background-color: {ACCENT};
            selection-color: white;
        }}

        QTextEdit QScrollBar:vertical {{
            background: transparent;
            width: 6px;
            margin: 8px 2px;
            border: none;
        }}

        QTextEdit QScrollBar::handle:vertical {{
            background: {BORDER2};
            border-radius: 3px;
            min-height: 30px;
        }}

        QTextEdit QScrollBar::handle:vertical:hover {{
            background: {TEXT4};
        }}

        QTextEdit QScrollBar::add-line:vertical,
        QTextEdit QScrollBar::sub-line:vertical {{
            height: 0px;
        }}

        QTextEdit QScrollBar::add-page:vertical,
        QTextEdit QScrollBar::sub-page:vertical {{
            background: none;
        }}

        QProgressBar {{
            border: none;
            border-radius: 3px;
            background-color: {BORDER};
            height: 4px;
            text-align: center;
            margin: 0px;
            color: transparent;
        }}

        QProgressBar::chunk {{
            background-color: {ACCENT};
            border-radius: 3px;
        }}

        QLabel {{
            color: {TEXT1};
            font-size: 13px;
            background-color: transparent;
        }}

        #statusLabel {{
            color: {TEXT1};
            font-size: 12px;
            font-weight: 400;
            margin: 0px;
        }}

        #textContainer {{
            background-color: transparent;
            margin: 0px;
        }}

        QMessageBox {{
            background-color: {SURFACE};
        }}

        QMessageBox QLabel {{
            color: {TEXT1};
            font-size: 13px;
        }}

        QMessageBox QPushButton {{
            min-width: 80px;
            padding: 8px 16px;
        }}
    """


def get_dialog_stylesheet(check_icon_path: str = "") -> str:
    x = check_icon_path
    return f"""
        QDialog {{
            background-color: {BG};
        }}
        * {{
            font-family: -apple-system, "SF Pro Display", "Helvetica Neue", sans-serif;
            color: {TEXT1};
        }}
        QWidget {{
            background-color: transparent;
        }}
        QScrollArea, QStackedWidget {{
            background-color: transparent;
            border: none;
        }}
        QScrollBar:vertical {{
            background: transparent;
            width: 5px;
            margin: 0;
        }}
        QScrollBar::handle:vertical {{
            background: {BORDER2};
            border-radius: 2px;
            min-height: 30px;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}
        QLineEdit {{
            background-color: {SURFACE2};
            color: {TEXT1};
            border: 1px solid {BORDER};
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 13px;
            selection-background-color: {ACCENT};
        }}
        QLineEdit:focus {{ border: 1px solid {ACCENT}; background-color: #1e2229; }}
        QCheckBox {{
            color: {TEXT1};
            font-size: 12px;
            spacing: 8px;
            padding: 4px 6px;
            border-radius: 5px;
        }}
        QCheckBox:hover {{ background-color: {SURFACE2}; color: {TEXT1}; }}
        QCheckBox::indicator {{
            width: 15px; height: 15px;
            border-radius: 4px;
            border: 1.5px solid {BORDER2};
            background-color: {SURFACE2};
        }}
        QCheckBox::indicator:checked {{
            background-color: {ACCENT};
            border: 1.5px solid {ACCENT};
            image: url("{x}");
        }}
        QCheckBox::indicator:checked:hover {{
            background-color: {ACCENT_H};
            image: url("{x}");
        }}
        QCheckBox::indicator:hover {{ border: 1.5px solid {ACCENT}; }}
        QPushButton {{
            background-color: {ACCENT};
            color: white;
            border: 1px solid {ACCENT_H};
            padding: 9px 22px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 500;
        }}
        QPushButton:hover {{ background-color: {ACCENT_H}; }}
        QPushButton:pressed {{ background-color: #005bb5; }}
        QPushButton#ghost {{
            background-color: transparent;
            color: {TEXT1};
            border: 1px solid {BORDER};
            font-weight: 400;
            padding: 7px 14px;
            font-size: 12px;
            min-width: 0;
        }}
        QPushButton#ghost:hover {{ background-color: {SURFACE2}; color: {TEXT1}; border-color: {BORDER2}; }}
        QPushButton#cancel {{
            background-color: {SURFACE2};
            color: {TEXT1};
            border: 1px solid {BORDER};
            font-weight: 400;
            min-width: 80px;
        }}
        QPushButton#cancel:hover {{ background-color: {SURFACE}; color: {TEXT1}; }}
        QListWidget {{
            background-color: {SURFACE};
            border: none;
            border-radius: 10px;
            padding: 6px 4px;
            outline: none;
        }}
        QListWidget::item {{
            border-radius: 7px;
            padding: 0px;
            margin: 1px 4px;
            color: {TEXT1};
            font-size: 13px;
        }}
        QListWidget::item:selected {{ background-color: {ACCENT}; color: white; }}
        QListWidget::item:hover:!selected {{ background-color: {SURFACE2}; color: {TEXT1}; }}
        QListWidget QScrollBar:vertical,
        QListWidget QScrollBar:horizontal {{
            width: 0px;
            height: 0px;
            background: transparent;
        }}
        QListWidget QScrollBar::handle:vertical,
        QListWidget QScrollBar::handle:horizontal {{
            background: transparent;
        }}
        QListWidget QScrollBar::add-line:vertical,
        QListWidget QScrollBar::sub-line:vertical,
        QListWidget QScrollBar::add-line:horizontal,
        QListWidget QScrollBar::sub-line:horizontal {{
            height: 0px;
            width: 0px;
        }}
    """