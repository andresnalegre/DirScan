from PyQt5.QtCore import QThread, pyqtSignal
from datetime import datetime
import os
import sys
from dirscan.utils import count_items, filter_items

sys.setrecursionlimit(5000)

CONNECTOR_LAST   = "└── "
CONNECTOR_MIDDLE = "├── "
PREFIX_LAST      = "    "
PREFIX_MIDDLE    = "│   "


class MapperThread(QThread):
    progress_signal  = pyqtSignal(int)
    status_signal    = pyqtSignal(str)
    finished_signal  = pyqtSignal(bool)
    text_signal      = pyqtSignal(str)

    def __init__(self, folder_path, ignore_temp_files):
        super().__init__()
        self.folder_path       = folder_path
        self.ignore_temp_files = ignore_temp_files
        self.total_items       = 0
        self.processed_items   = 0
        self._buffer           = []
        self._BATCH_SIZE       = 20

    def _flush(self):
        if self._buffer:
            self.text_signal.emit("".join(self._buffer))
            self._buffer.clear()

    def _emit_line(self, line: str):
        self._buffer.append(line)
        if len(self._buffer) >= self._BATCH_SIZE:
            self._flush()

    def _update_progress(self, name: str):
        self.processed_items += 1
        pct = int(self.processed_items * 100 / self.total_items)
        self.progress_signal.emit(min(pct, 100))
        self.status_signal.emit(f"Processing: {name}")

    def map_directory(self, path, prefix=""):
        try:
            items = os.listdir(path)
        except PermissionError:
            self._emit_line(prefix + CONNECTOR_LAST + "⚠️ Access denied\n")
            return
        except Exception as e:
            self._emit_line(prefix + CONNECTOR_LAST + f"⚠️ Error: {e}\n")
            return

        folders, files = filter_items(items, path, self.ignore_temp_files)

        all_entries = [("folder", f) for f in folders] + \
                      [("file",   f) for f in files if f != "map.txt"]

        for idx, (kind, name) in enumerate(all_entries):
            is_last   = (idx == len(all_entries) - 1)
            connector = CONNECTOR_LAST if is_last else CONNECTOR_MIDDLE
            icon      = "📁" if kind == "folder" else "📄"

            self._emit_line(f"{prefix}{connector}{icon} {name}\n")
            self._update_progress(name)

            if kind == "folder":
                extension = PREFIX_LAST if is_last else PREFIX_MIDDLE
                try:
                    self.map_directory(os.path.join(path, name), prefix + extension)
                except RecursionError:
                    self._emit_line(prefix + extension + CONNECTOR_LAST + "⚠️ Max depth reached\n")

    def run(self):
        self.total_items     = count_items(self.folder_path, self.ignore_temp_files)
        self.processed_items = 0
        directory_name       = os.path.basename(self.folder_path) or self.folder_path

        self._emit_line(f"Directory: {directory_name}\n")
        self._emit_line(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        self._emit_line(f"Root folder: {self.folder_path}\n")
        self._emit_line("-" * 50 + "\n\n")
        self._emit_line(f"📁 {directory_name}\n")

        self.map_directory(self.folder_path)

        self._emit_line("\n" + "-" * 50 + "\n")
        self._flush()

        self.progress_signal.emit(100)
        self.finished_signal.emit(True)