import sys
from PyQt5.QtWidgets import QApplication
from dirscan.ui import DirectoryMapperGUI

sys.setrecursionlimit(5000)

def main():
    app = QApplication(sys.argv)
    ex = DirectoryMapperGUI()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()