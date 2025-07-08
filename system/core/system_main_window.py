from PySide6.QtWidgets import QMainWindow, QApplication
from PySide6.QtCore import Qt
from enum import Enum

from .log import *
from core.wallpaper import Wallpaper

class WindowMode(Enum):
    WINDOWED = 0
    MAXIMIZED = 1
    MINIMIZED = 2
    FULLSCREEN = 3

class SystemMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LSystem 013")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: black;")

        self.wallpaper = None

        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(0, 0, screen.width(), screen.height())

        LOG_INFO("Window size: {}x{}", self.width(), self.height())
    
    def set_wallpaper(self, wp_path):
        try:
            self.wallpaper = Wallpaper(wp_path, parent=self)
            self.wallpaper.lower()
        except Exception as e:
            LOG_FATAL("Failed to initialize wallpaper: {}", e)

        LOG_INFO("Wallpaper size: {}x{}", 
          self.wallpaper.width(),
          self.wallpaper.height())
    
    def resizeEvent(self, event):
        if self.wallpaper and hasattr(self, 'wallpaper'):
            self.wallpaper.update_wallpaper(self.width(), self.height())
            
            self.wallpaper.setGeometry(0, 0, self.width(), self.height())
            
        super().resizeEvent(event)
    
    def show(self, mode: WindowMode):
        if mode == WindowMode.WINDOWED:
            self.showNormal()
        if mode == WindowMode.MAXIMIZED:
            self.showMaximized()
        if mode == WindowMode.MINIMIZED:
            self.showMinimized()
        if mode == WindowMode.FULLSCREEN:
            self.showFullScreen()