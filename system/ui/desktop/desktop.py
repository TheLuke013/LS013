from PySide6.QtWidgets import QLabel, QSizePolicy, QWidget, QVBoxLayout, QMenu
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction

from core.constants import *
from ui.wallpaper import Wallpaper
from ui.wallpaper_selector import WallpaperSelector

class Desktop(QWidget):
    wallpaper_change_requested = Signal(str)
    
    def __init__(self, username, main_window):
        super().__init__()
        self.username = username
        self.main_window = main_window
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
             
        self.main_window.change_wallpaper(DEFAULT_DESKTOP_WALLPAPER_FILENAME)
        
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        
        self.taskbar = QLabel(self)
        self.taskbar.setGeometry(0, self.height() - 40, self.width(), 40)
        self.taskbar.setStyleSheet("background-color: rgba(0, 0, 0, 150); color: white;")
        self.taskbar.setText(f"Usu√°rio: {self.username} | LSystem 013")
        
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
    def show_context_menu(self, pos):
        menu = QMenu(self)
        
        change_wallpaper_action = QAction("Trocar Papel de Parede", self)
        change_wallpaper_action.triggered.connect(self.open_wallpaper_selector)
        menu.addAction(change_wallpaper_action)
        
        menu.exec_(self.mapToGlobal(pos))
    
    def open_wallpaper_selector(self):
        self.wallpaper_selector = WallpaperSelector("")
        self.wallpaper_selector.wallpaper_selected.connect(self.change_wallpaper_requested)
        self.wallpaper_selector.show()
    
    def change_wallpaper_requested(self, new_wallpaper_path):
        self.wallpaper_change_requested.emit(new_wallpaper_path)
        

     