import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget


def main():
    app = QApplication([])
    window = QWidget()
    window.show()
    app.exec_()
    

if __name__ == '__main__':
    main()