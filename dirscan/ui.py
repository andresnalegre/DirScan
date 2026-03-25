from PyQt5.QtWidgets import (QMainWindow, QPushButton, QTextEdit, QVBoxLayout,
                             QHBoxLayout, QWidget, QFileDialog, QProgressBar,
                             QLabel, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from dirscan.styles import get_stylesheet
from dirscan.logics import MapperThread
import os


class DirectoryMapperGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.folder_path   = None
        self.mapper_thread = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('DirScan')
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet(get_stylesheet())
        self.setWindowIcon(self.load_icon())

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        button_container = QWidget()
        button_container.setObjectName("buttonContainer")
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)

        self.select_button = QPushButton('Select Folder', self)
        self.select_button.setObjectName("selectButton")
        self.select_button.clicked.connect(self.select_folder)

        self.save_button = QPushButton('Save', self)
        self.save_button.setObjectName("saveButton")
        self.save_button.clicked.connect(self.save_map)
        self.save_button.setEnabled(False)

        button_layout.addWidget(self.select_button)
        button_layout.addWidget(self.save_button)
        layout.addWidget(button_container)

        text_container = QWidget()
        text_container.setObjectName("textContainer")
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)

        self.text_edit = QTextEdit()
        self.text_edit.setObjectName("textEdit")
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont('Consolas', 11))
        text_layout.addWidget(self.text_edit)
        layout.addWidget(text_container)

        bottom_container = QWidget()
        bottom_layout = QVBoxLayout(bottom_container)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(5)

        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progressBar")
        self.progress_bar.setMaximum(100)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        bottom_layout.addWidget(self.progress_bar)

        self.status_label = QLabel('Ready')
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignCenter)
        bottom_layout.addWidget(self.status_label)

        layout.addWidget(bottom_container)

    def load_icon(self):
        candidates = [
            os.path.join(os.path.dirname(__file__), '..', 'assets', 'logo.icns'),
            os.path.join(os.path.dirname(__file__), 'assets', 'logo.icns'),
            os.path.join(os.path.dirname(__file__), '..', 'logo.icns'),
        ]
        for path in candidates:
            path = os.path.normpath(path)
            if os.path.isfile(path):
                icon = QIcon(path)
                if not icon.isNull():
                    return icon
        return QIcon()

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select a Folder")
        if not folder:
            return

        self.folder_path = folder

        message_box = QMessageBox(self)
        message_box.setWindowTitle('Ignore Temporary Files')
        message_box.setText(
            "Do you want to ignore temporary files like .DS_Store, .git, "
            "node_modules, venv, __pycache__, and log files?"
        )
        message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        message_box.setDefaultButton(QMessageBox.No)
        message_box.setStyleSheet("""
            QMessageBox { background-color: #1a1a1a; }
            QLabel      { color: white; font-size: 13px; }
            QPushButton {
                background-color: #2196F3; color: white; border: none;
                padding: 8px 16px; border-radius: 4px; min-width: 100px;
            }
            QPushButton:hover { background-color: #1976D2; }
        """)
        reply = message_box.exec_()
        ignore_temp_files = (reply == QMessageBox.Yes)

        self.text_edit.clear()
        self.progress_bar.setValue(0)
        self.save_button.setEnabled(False)
        self.select_button.setEnabled(False)
        self.status_label.setText("Starting…")

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

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Map", "",
            "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.text_edit.toPlainText())
                self.status_label.setText(f"Map saved: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error saving the file:\n{str(e)}")