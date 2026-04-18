from PyQt5.QtWidgets import (
    QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout,
    QWidget, QFileDialog, QProgressBar, QLabel, QMessageBox,
    QDialog, QCheckBox, QScrollArea, QLineEdit, QFrame,
    QListWidget, QListWidgetItem, QStackedWidget,
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QSize, QThread
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor
from dirscan.styles import (
    get_stylesheet, get_dialog_stylesheet,
    BG, SURFACE, SURFACE2, BORDER, BORDER2, ACCENT, GREEN, TEXT1, TEXT2, TEXT3, TEXT4,
)
from dirscan.logics import MapperThread
from dirscan.utils import FilterConfig, ALL_CATEGORIES, PREFIX_SET
import os


def _check_icon_path() -> str:
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "assets", "x.png")


class DiscoveryThread(QThread):
    finished = pyqtSignal(set, set, set)

    def __init__(self, root: str):
        super().__init__()
        self.root = root

    def run(self):
        found_folders:    set[str] = set()
        found_filenames:  set[str] = set()
        found_extensions: set[str] = set()
        try:
            for dirpath, dirnames, filenames in os.walk(self.root, followlinks=False):
                for d in dirnames:
                    found_folders.add(d)
                for f in filenames:
                    found_filenames.add(f)
                    _, ext = os.path.splitext(f)
                    if ext:
                        found_extensions.add(ext.lower())
        except Exception as e:
            print(f"[DirScan] Discovery error: {e}")
        self.finished.emit(found_folders, found_filenames, found_extensions)


class CategoryPage(QWidget):
    counts_changed = pyqtSignal()

    def __init__(self, item_kind_map: dict):
        super().__init__()
        self.item_kind_map = item_kind_map
        self.checks: dict[str, QCheckBox] = {}
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        inner = QWidget()
        inner.setStyleSheet("background: transparent;")
        inner_layout = QVBoxLayout(inner)
        inner_layout.setContentsMargins(12, 8, 12, 12)
        inner_layout.setSpacing(1)
        for item in sorted(self.item_kind_map.keys()):
            cb = QCheckBox(item)
            cb.setChecked(True)
            cb.stateChanged.connect(self.counts_changed.emit)
            self.checks[item] = cb
            inner_layout.addWidget(cb)
        inner_layout.addStretch()
        scroll.setWidget(inner)
        layout.addWidget(scroll)

    def apply_search(self, query: str):
        q = query.strip().lower()
        for item, cb in self.checks.items():
            cb.setVisible(not q or q in item.lower())

    def set_all_visible(self, state: bool, query: str = ""):
        q = query.strip().lower()
        for item, cb in self.checks.items():
            if not q or q in item.lower():
                cb.setChecked(state)

    def reset(self):
        for cb in self.checks.values():
            cb.setChecked(True)

    def get_ignored(self) -> frozenset:
        return frozenset(k for k, cb in self.checks.items() if cb.isChecked())

    def count_checked(self) -> int:
        return sum(1 for cb in self.checks.values() if cb.isChecked())

    def count_visible(self) -> int:
        return sum(1 for cb in self.checks.values() if cb.isVisible())

    def count_total(self) -> int:
        return len(self.checks)


class FilterDialog(QDialog):
    def __init__(self, root_path: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("DirScan")
        self.setMinimumSize(820, 580)
        self.resize(860, 620)
        self.setStyleSheet(get_dialog_stylesheet(_check_icon_path()))

        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(120)
        self._search_timer.timeout.connect(self._do_search)

        self._active_cats: list[dict]         = []
        self._active_maps: list[dict]         = []
        self._pages:       list[CategoryPage] = []

        self._build_shell()

        self._discovery = DiscoveryThread(root_path)
        self._discovery.finished.connect(self._on_discovery_done)
        self._discovery.start()

    def _build_shell(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        sidebar = QWidget()
        sidebar.setFixedWidth(210)
        sidebar.setStyleSheet(f"background-color: {SURFACE};")
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(12, 24, 12, 20)
        sb_layout.setSpacing(4)

        sb_title = QLabel("CATEGORIES")
        sb_title.setStyleSheet(
            f"font-size: 10px; font-weight: 700; color: {TEXT1}; "
            f"letter-spacing: 1.2px; padding-left: 6px; padding-bottom: 6px;"
        )
        sb_layout.addWidget(sb_title)

        self._nav = QListWidget()
        self._nav.setFocusPolicy(Qt.NoFocus)
        self._nav.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._nav.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._nav.currentRowChanged.connect(self._switch_page)
        sb_layout.addWidget(self._nav, 1)

        sb_layout.addSpacing(12)
        self._sidebar_summary = QLabel()
        self._sidebar_summary.setStyleSheet(
            f"font-size: 11px; color: {TEXT1}; padding-left: 6px; line-height: 160%;"
        )
        self._sidebar_summary.setWordWrap(True)
        self._sidebar_summary.setVisible(False)
        sb_layout.addWidget(self._sidebar_summary)

        root.addWidget(sidebar)

        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setStyleSheet(f"background: {BORDER}; max-width: 1px; border: none;")
        root.addWidget(sep)

        main = QWidget()
        main.setStyleSheet(f"background-color: {BG};")
        self._main_layout = QVBoxLayout(main)
        self._main_layout.setContentsMargins(24, 24, 24, 20)
        self._main_layout.setSpacing(0)

        self._page_title = QLabel("Analysing…")
        self._page_title.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {TEXT1};")
        self._page_desc = QLabel("Scanning your project to find relevant filters.")
        self._page_desc.setStyleSheet(f"font-size: 12px; color: {TEXT1}; line-height: 150%;")
        self._page_desc.setWordWrap(True)
        self._main_layout.addWidget(self._page_title)
        self._main_layout.addSpacing(4)
        self._main_layout.addWidget(self._page_desc)
        self._main_layout.addSpacing(16)

        search_row = QHBoxLayout()
        search_row.setSpacing(8)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search in this category…")
        self.search.textChanged.connect(self._search_timer.start)
        self.search.setClearButtonEnabled(True)
        self.search.setEnabled(False)
        search_row.addWidget(self.search, 1)
        self._btn_all = QPushButton("Select all")
        self._btn_all.setObjectName("ghost")
        self._btn_all.setEnabled(False)
        self._btn_all.clicked.connect(lambda: self._set_all_current(True))
        self._btn_none = QPushButton("Deselect all")
        self._btn_none.setObjectName("ghost")
        self._btn_none.setEnabled(False)
        self._btn_none.clicked.connect(lambda: self._set_all_current(False))
        search_row.addWidget(self._btn_all)
        search_row.addWidget(self._btn_none)
        self._main_layout.addLayout(search_row)
        self._main_layout.addSpacing(8)

        self._status_label = QLabel()
        self._status_label.setStyleSheet(f"font-size: 11px; color: {TEXT1};")
        self._main_layout.addWidget(self._status_label)
        self._main_layout.addSpacing(8)

        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet(f"background: {BORDER}; max-height: 1px; border: none;")
        self._main_layout.addWidget(div)
        self._main_layout.addSpacing(4)

        self.stack = QStackedWidget()
        self._main_layout.addWidget(self.stack, 1)

        self._main_layout.addSpacing(8)
        bot_div = QFrame()
        bot_div.setFrameShape(QFrame.HLine)
        bot_div.setStyleSheet(f"background: {BORDER}; max-height: 1px; border: none;")
        self._main_layout.addWidget(bot_div)
        self._main_layout.addSpacing(12)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        self._btn_reset = QPushButton("Reset to defaults")
        self._btn_reset.setObjectName("ghost")
        self._btn_reset.setEnabled(False)
        self._btn_reset.clicked.connect(self._reset_all)
        btn_cancel = QPushButton("Cancel")
        btn_cancel.setObjectName("cancel")
        btn_cancel.clicked.connect(self.reject)
        self._btn_scan = QPushButton("  Start  ")
        self._btn_scan.setEnabled(False)
        self._btn_scan.clicked.connect(self.accept)
        btn_row.addWidget(self._btn_reset)
        btn_row.addStretch()
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(self._btn_scan)
        self._main_layout.addLayout(btn_row)

        root.addWidget(main, 1)

    def _on_discovery_done(self, found_folders: set, found_files: set, found_exts: set):
        for cat in ALL_CATEGORIES:
            relevant: dict[str, str] = {}
            for item, kind in cat["items"].items():
                if kind == "folder" and item in found_folders:
                    relevant[item] = kind
                elif kind == "file" and item in found_files:
                    relevant[item] = kind
                elif kind == "ext" and item in found_exts:
                    relevant[item] = kind
                elif kind == "pattern":
                    relevant[item] = kind
            if relevant:
                self._active_cats.append(cat)
                self._active_maps.append(relevant)
        self._populate_pages()

    def _populate_pages(self):
        self._nav.clear()
        self._pages.clear()
        while self.stack.count():
            w = self.stack.widget(0)
            self.stack.removeWidget(w)
            w.deleteLater()

        if not self._active_cats:
            self._page_title.setText("Nothing to filter")
            self._page_desc.setText("No known noise was found in this project.\nAll files and folders will be included.")
            self._btn_scan.setEnabled(True)
            return

        for cat, item_kind_map in zip(self._active_cats, self._active_maps):
            page = CategoryPage(item_kind_map)
            page.counts_changed.connect(self._refresh_status)
            self._pages.append(page)
            self.stack.addWidget(page)
            nav_item = QListWidgetItem(f"  {cat['icon']}  {cat['name']}")
            nav_item.setSizeHint(QSize(185, 40))
            self._nav.addItem(nav_item)

        self.search.setEnabled(True)
        self._btn_all.setEnabled(True)
        self._btn_none.setEnabled(True)
        self._btn_reset.setEnabled(True)
        self._btn_scan.setEnabled(True)
        self._nav.setCurrentRow(0)
        self._refresh_status()

    def _switch_page(self, idx: int):
        if 0 <= idx < len(self._pages):
            self.stack.setCurrentIndex(idx)
            self.search.clear()
            self._do_search()
            cat = self._active_cats[idx]
            self._page_title.setText(cat["name"])
            self._page_desc.setText(cat["desc"])
            self._refresh_status()

    def _do_search(self):
        idx = self.stack.currentIndex()
        if 0 <= idx < len(self._pages):
            self._pages[idx].apply_search(self.search.text())
        self._refresh_status()

    def _set_all_current(self, state: bool):
        idx = self.stack.currentIndex()
        if 0 <= idx < len(self._pages):
            self._pages[idx].set_all_visible(state, self.search.text())
        self._refresh_status()

    def _reset_all(self):
        for page in self._pages:
            page.reset()
        self.search.clear()
        self._do_search()
        self._refresh_status()

    def _refresh_status(self):
        idx = self.stack.currentIndex()
        if not (0 <= idx < len(self._pages)):
            return
        page    = self._pages[idx]
        checked = page.count_checked()
        total   = page.count_total()
        visible = page.count_visible()
        q       = self.search.text().strip()
        if q:
            self._status_label.setText(
                f"<span style='color:{TEXT1}'>{visible} matching</span>"
                f"&nbsp;·&nbsp;"
                f"<span style='color:{GREEN}'>{checked}</span>"
                f"<span style='color:{TEXT1}'> of {total} selected to ignore</span>"
            )
        else:
            self._status_label.setText(
                f"<span style='color:{GREEN}'>{checked}</span>"
                f"<span style='color:{TEXT1}'> of {total} items selected to ignore</span>"
            )
        for i, cat in enumerate(self._active_cats):
            p = self._pages[i]
            c, t = p.count_checked(), p.count_total()
            item = self._nav.item(i)
            if item:
                item.setText(f"  {cat['icon']}  {cat['name']}  ({c}/{t})")
        total_checked = sum(p.count_checked() for p in self._pages)
        total_all     = sum(p.count_total()   for p in self._pages)
        self._sidebar_summary.setText(
            f"<span style='color:{GREEN};font-weight:600'>{total_checked}</span>"
            f"<span style='color:{TEXT1}'> / {total_all} items<br>will be ignored</span>"
        )
        self._sidebar_summary.setVisible(True)

    def closeEvent(self, event):
        event.accept()
        from PyQt5.QtWidgets import QApplication
        QApplication.quit()

    def get_config(self) -> FilterConfig:
        all_folders:    set[str] = set()
        all_filenames:  set[str] = set()
        all_extensions: set[str] = set()
        prefixes: list[str] = []
        suffixes: list[str] = []
        for cat, item_kind_map, page in zip(self._active_cats, self._active_maps, self._pages):
            for item in page.get_ignored():
                kind = item_kind_map.get(item, "folder")
                if kind == "folder":
                    all_folders.add(item)
                elif kind == "file":
                    all_filenames.add(item)
                elif kind == "ext":
                    all_extensions.add(item)
                elif kind == "pattern":
                    if item in PREFIX_SET:
                        prefixes.append(item)
                    else:
                        suffixes.append(item)
        return FilterConfig(
            folders    = frozenset(all_folders),
            filenames  = frozenset(all_filenames),
            extensions = frozenset(all_extensions),
            prefixes   = tuple(prefixes),
            suffixes   = tuple(suffixes),
        )


class DirectoryMapperGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.folder_path   = None
        self.mapper_thread = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('DirScan')
        self.setGeometry(100, 100, 860, 620)
        self.setMinimumSize(680, 480)
        self.setStyleSheet(get_stylesheet())
        self.setWindowIcon(self._load_icon())

        palette = self.palette()
        palette.setColor(QPalette.WindowText, QColor('#f5f5f7'))
        self.setPalette(palette)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        toolbar = QWidget()
        toolbar.setObjectName("buttonContainer")
        toolbar.setFixedHeight(64)
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(24, 0, 24, 0)
        tb_layout.setSpacing(12)

        left_spacer = QWidget()
        left_spacer.setFixedSize(28, 28)
        left_spacer.setStyleSheet("background: transparent;")
        tb_layout.addWidget(left_spacer)

        tb_layout.addStretch()

        self.select_button = QPushButton("  Select Folder  ")
        self.select_button.setObjectName("selectButton")
        self.select_button.setFixedHeight(38)
        self.select_button.clicked.connect(self.select_folder)

        self.save_button = QPushButton("  Save  ")
        self.save_button.setObjectName("saveButton")
        self.save_button.setFixedHeight(38)
        self.save_button.clicked.connect(self.save_map)
        self.save_button.setEnabled(False)

        tb_layout.addWidget(self.select_button)
        tb_layout.addWidget(self.save_button)

        tb_layout.addStretch()

        _info_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "info.png")
        self.info_button = QPushButton()
        self.info_button.setFixedSize(28, 28)
        self.info_button.setIconSize(QSize(28, 28))
        self.info_button.setIcon(QIcon(_info_path))
        self.info_button.setStyleSheet(
            "QPushButton { background: transparent; border: none; padding: 0px; }"
            "QPushButton:pressed { background: transparent; border: none; }"
        )
        self.info_button.clicked.connect(self.show_about)
        tb_layout.addWidget(self.info_button)

        root.addWidget(toolbar)

        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet(f"background: {BORDER}; max-height: 1px; border: none;")
        root.addWidget(div)

        body = QWidget()
        body.setStyleSheet(f"background-color: {BG};")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(24, 20, 24, 20)
        body_layout.setSpacing(0)

        self.text_edit = QTextEdit()
        self.text_edit.setObjectName("textEdit")
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont('Menlo', 12))
        body_layout.addWidget(self.text_edit, 1)

        root.addWidget(body, 1)

        status_bar = QWidget()
        status_bar.setFixedHeight(52)
        status_bar.setStyleSheet(
            f"background-color: {SURFACE}; border-top: 1px solid {BORDER};"
        )
        sb_layout = QHBoxLayout(status_bar)
        sb_layout.setContentsMargins(20, 0, 20, 0)
        sb_layout.setSpacing(16)

        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("statusLabel")
        sb_layout.addWidget(self.status_label, 1)

        progress_wrap = QWidget()
        progress_wrap.setStyleSheet("background: transparent; border: none;")
        pw_layout = QVBoxLayout(progress_wrap)
        pw_layout.setContentsMargins(0, 0, 0, 0)
        pw_layout.setSpacing(3)

        self._pct_label = QLabel("0%")
        self._pct_label.setAlignment(Qt.AlignRight)
        self._pct_label.setStyleSheet(
            "font-size: 11px; color: #f5f5f7; background: transparent; border: none;"
        )
        pw_layout.addWidget(self._pct_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progressBar")
        self.progress_bar.setMaximum(100)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedWidth(160)
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet(
            "QProgressBar { border: none; border-top: none; border-radius: 3px;"
            " background-color: #2c2c2e; margin: 0px; padding: 0px; }"
            "QProgressBar::chunk { background-color: #0a84ff; border-radius: 3px; }"
        )
        pw_layout.addWidget(self.progress_bar)

        sb_layout.addWidget(progress_wrap, 0, Qt.AlignVCenter)
        root.addWidget(status_bar)

    def _load_icon(self):
        base = os.path.dirname(__file__)
        for name in ('logo.icns', 'logo.ico', 'logo.png'):
            path = os.path.normpath(os.path.join(base, 'assets', name))
            if os.path.isfile(path):
                icon = QIcon(path)
                if not icon.isNull():
                    return icon
        return QIcon()

    def closeEvent(self, event):
        if self.mapper_thread and self.mapper_thread.isRunning():
            self.mapper_thread.cancel()
            self.mapper_thread.quit()
            self.mapper_thread.wait()
        event.accept()

    def show_about(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("About")
        dialog.setFixedSize(420, 300)
        dialog.setStyleSheet(f"""
            QDialog {{
                background-color: {BG};
            }}
            QLabel {{
                background: transparent;
                border: none;
            }}
            QPushButton#okBtn {{
                background-color: #0a84ff;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 8px 0px;
                font-size: 13px;
                font-weight: 600;
                min-width: 100px;
                max-width: 100px;
            }}
            QPushButton#okBtn:hover {{
                background-color: #1a8fff;
            }}
            QPushButton#okBtn:pressed {{
                background-color: #0060cc;
            }}
        """)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(32, 32, 32, 28)
        layout.setSpacing(0)

        title = QLabel("DirScan")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"font-size: 22px; font-weight: 700; color: {TEXT1};")
        layout.addWidget(title)

        layout.addSpacing(16)

        desc = QLabel(
            "DirScan is the ultimate tool for scanning folders and generating "
            "clean, visual tree structures. Apply filters to exclude unnecessary "
            "files and export the result as a .txt file."
        )
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet(f"font-size: 13px; color: {TEXT2}; line-height: 160%;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addSpacing(24)

        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet(f"background: {BORDER}; max-height: 1px; border: none;")
        layout.addWidget(div)

        layout.addSpacing(16)

        built_row = QHBoxLayout()
        built_row.setSpacing(6)
        built_row.addStretch()

        py_badge = QLabel("Python")
        py_badge.setStyleSheet(
            "font-size: 11px; font-weight: 600; color: #f5f5f7;"
            "background-color: #3572A5; border-radius: 4px; padding: 2px 8px;"
        )
        built_row.addWidget(py_badge)

        qt_badge = QLabel("PyQt5")
        qt_badge.setStyleSheet(
            "font-size: 11px; font-weight: 600; color: #f5f5f7;"
            "background-color: #41CD52; border-radius: 4px; padding: 2px 8px;"
        )
        built_row.addWidget(qt_badge)

        built_row.addStretch()
        layout.addLayout(built_row)

        layout.addSpacing(12)

        dev_link = QLabel(
            f'<span style="color: {TEXT3};">Developed by&nbsp;</span>'
            f'<a href="https://andresnicolas.com" '
            f'style="color: #0a84ff; text-decoration: none; font-weight: 600;">'
            f'Andres Nicolas</a>'
        )
        dev_link.setAlignment(Qt.AlignCenter)
        dev_link.setStyleSheet("font-size: 13px;")
        dev_link.setOpenExternalLinks(True)
        layout.addWidget(dev_link)

        layout.addStretch()

        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, 0, 0, 0)
        ok_btn = QPushButton("OK")
        ok_btn.setObjectName("okBtn")
        ok_btn.clicked.connect(dialog.accept)
        btn_row.addStretch()
        btn_row.addWidget(ok_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        dialog.exec_()

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select a Folder")
        if not folder:
            return
        self.folder_path = folder

        dialog = FilterDialog(self.folder_path, self)
        if dialog.exec_() != QDialog.Accepted:
            return

        config = dialog.get_config()
        self.text_edit.clear()
        self.progress_bar.setValue(0)
        self._pct_label.setText("0%")
        self.save_button.setEnabled(False)
        self.select_button.setEnabled(False)
        self.status_label.setText("Starting…")

        if self.mapper_thread and self.mapper_thread.isRunning():
            self.mapper_thread.cancel()
            self.mapper_thread.quit()
            self.mapper_thread.wait()

        self.mapper_thread = MapperThread(self.folder_path, config)
        self.mapper_thread.progress_signal.connect(self._update_progress)
        self.mapper_thread.status_signal.connect(self.status_label.setText)
        self.mapper_thread.finished_signal.connect(self._on_finished)
        self.mapper_thread.text_signal.connect(self.text_edit.insertPlainText)
        self.mapper_thread.start()

    def _update_progress(self, value: int):
        self.progress_bar.setValue(value)
        self._pct_label.setText(f"{value}%")

    def _on_finished(self, success: bool):
        self.select_button.setEnabled(True)
        self.save_button.setEnabled(success)
        self.status_label.setText("Mapping completed!" if success else "Scan cancelled.")

    def save_map(self):
        if not self.folder_path:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Map", "", "Text Files (*.txt);;All Files (*)"
        )
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(self.text_edit.toPlainText())
                self.status_label.setText(f"Map saved: {path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save file:\n{e}")