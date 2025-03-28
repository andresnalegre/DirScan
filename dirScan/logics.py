import os
from datetime import datetime
from PyQt5.QtWidgets import (QMainWindow, QPushButton, QTextEdit, QVBoxLayout, 
                             QHBoxLayout, QWidget, QFileDialog, QProgressBar, 
                             QLabel, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
from dirScan.styles import get_stylesheet

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

    def count_items(self, path):
        total = 0
        try:
            for root, dirs, files in os.walk(path):
                total += len(dirs) + len(files)
        except:
            pass
        return total

    def map_directory(self, path, indent=0, is_last=True):
        try:
            items = os.listdir(path)
            folders = sorted([item for item in items if os.path.isdir(os.path.join(path, item))])
            files = sorted([item for item in items if os.path.isfile(os.path.join(path, item))])

            if self.ignore_temp_files:
                folders = [f for f in folders if f not in [
                    '.git', '.svn', '.hg', 'node_modules', 'venv', 'dist', 'build', 
                    'target', '.idea', '.vscode', '.Trash', '.cache', '__pycache__', 
                    'coverage'
                ]]
                files = [f for f in files if not (
                    f.startswith('.') or f.endswith('.log') or f.endswith('~') or 
                    f.endswith('.pyc') or f.endswith('.tmp') or f.endswith('.temp') or 
                    f in ['Thumbs.db', '.DS_Store', '.env', '.coverage']
                )]

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
        self.total_items = self.count_items(self.folder_path)
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

class DirectoryMapperGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('DirScan')
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet(get_stylesheet())

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        button_layout = QHBoxLayout()
        
        self.select_button = QPushButton('Select Folder', self)
        self.select_button.clicked.connect(self.select_folder)
        self.select_button.setIcon(QIcon('folder.png'))  # Ícone de pasta
        
        self.save_button = QPushButton('Save', self)
        self.save_button.clicked.connect(self.save_map)
        self.save_button.setEnabled(False)
        self.save_button.setIcon(QIcon('save.png'))  # Ícone de salvar

        button_layout.addWidget(self.select_button)
        button_layout.addWidget(self.save_button)
        layout.addLayout(button_layout)

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont('Consolas', 10))
        layout.addWidget(self.text_edit)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel('Ready')
        layout.addWidget(self.status_label)

        self.folder_path = None
        self.mapper_thread = None

    def select_folder(self):
        self.folder_path = QFileDialog.getExistingDirectory(self, "Select a Folder")
        if self.folder_path:
            message_box = QMessageBox(self)
            message_box.setWindowTitle('Ignore Temporary Files')
            message_box.setText("Do you want to ignore temporary files like .DS_Store, .git, node_modules, venv, __pycache__, and log files?")
            message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            message_box.setDefaultButton(QMessageBox.No)
            message_box.setStyleSheet("QLabel{color: white;}")
            reply = message_box.exec_()
            
            ignore_temp_files = reply == QMessageBox.Yes

            self.text_edit.clear()
            self.progress_bar.setValue(0)
            self.save_button.setEnabled(False)
            self.select_button.setEnabled(False)
            
            self.mapper_thread = MapperThread(self.folder_path, ignore_temp_files)
            self.mapper_thread.progress_signal.connect(self.update_progress)
            self.mapper_thread.status_signal.connect(self.update_status)
            self.mapper_thread.finished_signal.connect(self.mapping_finished)
            self.mapper_thread.text_signal.connect(self.append_text)
            self.mapper_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_status(self, status):
        self.status_label.setText(status)

    def append_text(self, text):
        self.text_edit.insertPlainText(text)

    def mapping_finished(self, success):
        self.select_button.setEnabled(True)
        self.save_button.setEnabled(True)
        self.status_label.setText("Mapping completed!")

    def save_map(self):
        if not self.folder_path:
            return

        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Map", "", "Text Files (*.txt);;All Files (*)", options=options)
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.text_edit.toPlainText())
                self.status_label.setText(f"Map saved successfully at: {file_path}")  # Atualiza a status_label
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error saving the file:\n{str(e)}")