from PySide6.QtWidgets import QApplication, QLabel, QMainWindow
from PySide6.QtCore import Qt
import sys
import os

import constants as CONSTS
from log import *
from wallpaper import Wallpaper

class LS013(QMainWindow):
    def __init__(self):
        #configure "low-level system"
        os.chdir(CONSTS.ROOT_PATH)

        #init logger
        Log.init()
        LOG_INFO("Initializing virtual system {} in: {}", CONSTS.SYSTEM_NAME, os.getcwd())

        super().__init__()
        self.setWindowTitle("LS013")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: black;")

        d_wp_path = os.path.abspath(os.path.join(CONSTS.DEFAULT_WALLPAPER_FILENAME))   

        try:
            self.default_wp = Wallpaper(d_wp_path, parent=self)
            self.default_wp.lower()
        except Exception as e:
            LOG_FATAL("Failed to initialize wallpaper: {}", e)
        
        self.showMaximized()

        LOG_INFO("Window size: {}x{}", self.width(), self.height())
        LOG_INFO("Wallpaper size: {}x{}", 
          self.default_wp.width(), 
          self.default_wp.height())

    def resizeEvent(self, event):
        if hasattr(self, 'default_wp'):
            self.default_wp.update_wallpaper(self.width(), self.height())
            
            self.default_wp.setGeometry(0, 0, self.width(), self.height())
            
        super().resizeEvent(event) 

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LS013()
    window.show()
    app.exec()