def get_stylesheet():
    return """
        QMainWindow {
            background-color: #f0f0f0;
        }
        QPushButton {
            background-color: #2196F3;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #1976D2;
        }
        QPushButton:disabled {
            background-color: #BDBDBD;
        }
        QTextEdit {
            background-color: white;
            color: black;
            border: 1px solid #BDBDBD;
            border-radius: 4px;
            padding: 8px;
        }
        QProgressBar {
            border: 1px solid #BDBDBD;
            border-radius: 4px;
            text-align: center;
        }
        QProgressBar::chunk {
            background-color: #4CAF50;
        }
        QLabel {
            color: #333;
        }
    """