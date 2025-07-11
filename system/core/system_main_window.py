from PySide6.QtWidgets import QMainWindow, QApplication
from PySide6.QtCore import Qt, QTimer
from enum import Enum

from .log import *
from system.ui.wallpaper import Wallpaper

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
    
    def change_wallpaper(self, new_wp_path):
        """Altera o wallpaper em tempo de execução"""
        try:
            if self.wallpaper:
                self.wallpaper.hide()
            
            new_wallpaper = Wallpaper(new_wp_path, parent=self)
            new_wallpaper.lower()
            
            if hasattr(self, 'wallpaper') and self.wallpaper:
                self.wallpaper.setParent(None)
                self.wallpaper.deleteLater()
            
            self.wallpaper = new_wallpaper
            
            self.wallpaper.update_wallpaper(self.width(), self.height())
            self.wallpaper.setGeometry(0, 0, self.width(), self.height())
            self.wallpaper.show()
            self.wallpaper.lower()
            
            LOG_INFO("Wallpaper changed to: {}", new_wp_path)
            return True
            
        except Exception as e:
            LOG_ERROR("Failed to change wallpaper: {}", e)
            if hasattr(self, 'wallpaper') and self.wallpaper:
                self.wallpaper.show()
            return False
            
    def hide_wallpaper(self):
        if self.wallpaper:
            self.wallpaper.hide()
        else:
            LOG_WARN("No wallpaper loaded to hide")

    def show_wallpaper(self):
        if self.wallpaper:
            self.wallpaper.show()
        else:
            LOG_WARN("No wallpaper loaded to show")

    def remove_wallpaper(self):
        if self.wallpaper:
            self.wallpaper.setParent(None)
            self.wallpaper.deleteLater()
            self.wallpaper = None
            LOG_WARN("Wallpaper was removed")
        else:
            LOG_WARN("No wallpaper loaded to remove")
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'wallpaper') and self.wallpaper:
            self.wallpaper.update_wallpaper(self.width(), self.height())
            self.wallpaper.setGeometry(0, 0, self.width(), self.height())
            self.wallpaper.lower()
    
    def show(self, mode: WindowMode):
        if mode == WindowMode.WINDOWED:
            self.showNormal()
        if mode == WindowMode.MAXIMIZED:
            self.showMaximized()
        if mode == WindowMode.MINIMIZED:
            self.showMinimized()
        if mode == WindowMode.FULLSCREEN:
            self.showFullScreen()