from PySide6.QtWidgets import QLabel, QSizePolicy, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from ui.wallpaper import Wallpaper
from core.constants import *

class Desktop(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.setWindowTitle("VirtualOS Desktop")
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Configurar wallpaper
        self.wallpaper = Wallpaper(DEFAULT_WALLPAPER_FILENAME, self)
        
        # Barra de tarefas (simplificada)
        self.taskbar = QLabel(self)
        self.taskbar.setGeometry(0, self.height() - 40, self.width(), 40)
        self.taskbar.setStyleSheet("background-color: rgba(0, 0, 0, 150); color: white;")
        self.taskbar.setText(f"Usuário: {self.username} | VirtualOS")
        
        # Mostrar desktop
        self.showMaximized()