def get_stylesheet():
    return """
        QMainWindow {
            background-color: #1e1e1e;
        }
        
        QWidget {
            background-color: #1e1e1e;
        }
        
        QPushButton {
            background-color: #2196F3;
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 14px;
            min-width: 150px;
        }
        
        QPushButton:hover {
            background-color: #1976D2;
        }
        
        QPushButton:pressed {
            background-color: #0D47A1;
        }
        
        QPushButton:disabled {
            background-color: #424242;
            color: #757575;
        }

        QPushButton#saveButton {
            background-color: #424242;
            color: #757575;
        }

        QPushButton#saveButton:enabled {
            background-color: #4CAF50;
            color: white;
        }

        QPushButton#saveButton:enabled:hover {
            background-color: #388E3C;
        }

        QPushButton#saveButton:enabled:pressed {
            background-color: #2E7D32;
        }
        
        QTextEdit {
            background-color: #e8e8e8;
            color: #2d2d2d;
            border: 1px solid #3d3d3d;
            border-radius: 8px;
            padding: 10px;
            font-family: 'Consolas';
            font-size: 13px;
            selection-background-color: #264f78;
        }
        
        QProgressBar {
            border: none;
            border-radius: 4px;
            background-color: #2d2d2d;
            height: 8px;
            text-align: center;
            margin: 0px;
        }
        
        QProgressBar::chunk {
            background-color: #4CAF50;
            border-radius: 4px;
        }
        
        QLabel {
            color: #ffffff;
            font-size: 14px;
        }
        
        QLabel#logo {
            background-color: transparent;
            margin: 0px;
            padding: 0px;
        }
        
        QLabel#title {
            color: white;
            font-size: 32px;
            font-weight: bold;
            margin-left: 10px;
        }
        
        #buttonContainer {
            background-color: transparent;
            margin: 5px 0px;
        }
        
        #statusLabel {
            color: #4CAF50;
            font-weight: bold;
            margin: 0px;
        }
        
        #textContainer {
            background-color: transparent;
            margin: 5px 0px;
        }

        QMessageBox {
            background-color: #1e1e1e;
        }
        
        QMessageBox QLabel {
            color: white;
            font-size: 13px;
        }
        
        QMessageBox QPushButton {
            min-width: 100px;
            padding: 8px 16px;
        }
        
        QFileDialog {
            background-color: #1e1e1e;
        }
        
        QFileDialog QLabel {
            color: white;
        }
        
        QFileDialog QPushButton {
            min-width: 100px;
        }
    """