from PySide6.QtWidgets import QApplication
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from core.system import LSystem013 

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ls013 = LSystem013()
    app.exec()