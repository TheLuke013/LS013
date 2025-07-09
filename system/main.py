from PySide6.QtWidgets import QApplication
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from core.system import LSystem013 
from core.flags import SystemFlags

if __name__ == "__main__":
    flags = SystemFlags.SKIP_SPLASH_SCREEN | SystemFlags.SKIP_SHUTDOWN_SCREEN #for develop tests
    #flags = SystemFlags.WINDOW_FULLSCREEN #for release
    #flags = SystemFlags.NONE

    app = QApplication(sys.argv)
    ls013 = LSystem013(flags)
    app.exec()