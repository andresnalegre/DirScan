from PyQt5.QtCore import QThread, pyqtSignal
from datetime import datetime
import os
from src.utils import count_items, filter_items

class MapperThread(QThread):
    progress_signal = pyqtSignal(int)
    status_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool)
    text_signal = pyqtSignal(str)

    def __init__(self, folder_path, ignore_temp_files):
        super().__init__()
        self.folder_path = folder_path
        self.ignore_temp_files = ignore_temp_files
        self.total_items = 0
        self.processed_items = 0

    def map_directory(self, path, indent=0, is_last=True):
        try:
            items = os.listdir(path)
            folders, files = filter_items(items, path, self.ignore_temp_files)

            for i, folder in enumerate(folders):
                folder_path = os.path.join(path, folder)
                connector = "└── " if is_last else "├── "
                self.text_signal.emit("    " * indent + connector + f"📁 {folder}\n")
                self.processed_items += 1
                self.progress_signal.emit(int(self.processed_items * 100 / self.total_items))
                self.status_signal.emit(f"Processing: {folder}")
                self.map_directory(folder_path, indent + 1, i == len(folders) - 1)

            for i, file in enumerate(files):
                if file != "map.txt":
                    connector = "└── " if is_last and i == len(files) - 1 else "├── "
                    self.text_signal.emit("    " * indent + connector + f"📄 {file}\n")
                    self.processed_items += 1
                    self.progress_signal.emit(int(self.processed_items * 100 / self.total_items))
                    self.status_signal.emit(f"Processing: {file}")

        except PermissionError:
            self.text_signal.emit("    " * indent + "⚠️ Access denied to this folder\n")
        except Exception as e:
            self.text_signal.emit("    " * indent + f"⚠️ Error accessing: {str(e)}\n")

    def run(self):
        self.total_items = count_items(self.folder_path)
        directory_name = os.path.basename(self.folder_path) or self.folder_path
        self.text_signal.emit(f"Directory: {directory_name}\n")
        self.text_signal.emit(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        self.text_signal.emit(f"Root folder: {self.folder_path}\n")
        self.text_signal.emit("-" * 50 + "\n\n")
        self.text_signal.emit(f"📁 {directory_name}\n")
        self.map_directory(self.folder_path, indent=1)
        self.progress_signal.emit(100)
        self.text_signal.emit("\n" + "-" * 50 + "\n")
        self.finished_signal.emit(True)