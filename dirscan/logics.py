from PyQt5.QtCore import QThread, pyqtSignal
from datetime import datetime
import os
from dirscan.utils import FilterConfig, count_items, filter_items

CONNECTOR_LAST   = "└── "
CONNECTOR_MIDDLE = "├── "
PREFIX_LAST      = "    "
PREFIX_MIDDLE    = "│   "

MAX_DEPTH = 200


class MapperThread(QThread):
    progress_signal = pyqtSignal(int)
    status_signal   = pyqtSignal(str)
    finished_signal = pyqtSignal(bool)
    text_signal     = pyqtSignal(str)

    def __init__(self, folder_path: str, config: FilterConfig):
        super().__init__()
        self.folder_path     = folder_path
        self.config          = config
        self.total_items     = 0
        self.processed_items = 0
        self._buffer         = []
        self._BATCH_SIZE     = 20
        self._cancelled      = False

    def cancel(self):
        self._cancelled = True

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

    def map_directory(self, root_path: str):
        """Iterative depth-first traversal preserving correct tree order."""
        # Each stack frame: (path, prefix, depth, entries, current_index)
        # We push a directory's entry list and iterate through it,
        # descending into subfolders immediately — preserving DFS order
        # without recursion.

        try:
            items = os.listdir(root_path)
        except PermissionError:
            self._emit_line(CONNECTOR_LAST + "⚠️ Access denied\n")
            return
        except Exception as e:
            self._emit_line(CONNECTOR_LAST + f"⚠️ Error: {e}\n")
            return

        folders, files = filter_items(items, root_path, self.config)
        all_entries = [("folder", f) for f in folders] + \
                      [("file",   f) for f in files if f != "map.txt"]

        stack = [(root_path, "", all_entries, 0, 0)]

        while stack and not self._cancelled:
            path, prefix, entries, idx, depth = stack[-1]

            if idx >= len(entries):
                stack.pop()
                continue

            stack[-1] = (path, prefix, entries, idx + 1, depth)

            kind, name = entries[idx]
            is_last    = (idx == len(entries) - 1)
            connector  = CONNECTOR_LAST if is_last else CONNECTOR_MIDDLE
            icon       = "📁" if kind == "folder" else "📄"
            self._emit_line(f"{prefix}{connector}{icon} {name}\n")
            self._update_progress(name)

            if kind == "folder":
                if depth >= MAX_DEPTH:
                    child_prefix = PREFIX_LAST if is_last else PREFIX_MIDDLE
                    self._emit_line(prefix + child_prefix + CONNECTOR_LAST + "⚠️ Max depth reached\n")
                    continue

                child_path   = os.path.join(path, name)
                child_prefix = prefix + (PREFIX_LAST if is_last else PREFIX_MIDDLE)

                try:
                    child_items = os.listdir(child_path)
                except PermissionError:
                    self._emit_line(child_prefix + CONNECTOR_LAST + "⚠️ Access denied\n")
                    continue
                except Exception as e:
                    self._emit_line(child_prefix + CONNECTOR_LAST + f"⚠️ Error: {e}\n")
                    continue

                child_folders, child_files = filter_items(child_items, child_path, self.config)
                child_entries = [("folder", f) for f in child_folders] + \
                                [("file",   f) for f in child_files if f != "map.txt"]

                if child_entries:
                    stack.append((child_path, child_prefix, child_entries, 0, depth + 1))

    def run(self):
        self.total_items     = count_items(self.folder_path, self.config)
        self.processed_items = 0
        directory_name       = os.path.basename(self.folder_path) or self.folder_path

        now = datetime.now().strftime('%d/%m/%Y - %H:%M:%S')
        self._emit_line(f"Directory: {directory_name}\n")
        self._emit_line(f"Date: {now}\n")
        self._emit_line(f"Location: {self.folder_path}\n")
        self._emit_line("-" * 50 + "\n\n")
        self._emit_line(f"📁 {directory_name}\n")

        self.map_directory(self.folder_path)

        if not self._cancelled:
            self._emit_line("\n" + "-" * 50 + "\n")
            self._flush()
            self.progress_signal.emit(100)
            self.finished_signal.emit(True)
        else:
            self._flush()
            self.finished_signal.emit(False)