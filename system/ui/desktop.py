from PySide6.QtWidgets import QMainWindow, QLabel, QDesktopWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from ui.wallpaper import Wallpaper

class Desktop(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.setWindowTitle("VirtualOS Desktop")
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        # Obter tamanho da tela
        screen = QDesktopWidget().screenGeometry()
        self.setGeometry(0, 0, screen.width(), screen.height())
        
        # Configurar wallpaper
        self.wallpaper = Wallpaper("assets/wallpapers/default.jpg", self)
        
        # Barra de tarefas (simplificada)
        self.taskbar = QLabel(self)
        self.taskbar.setGeometry(0, screen.height() - 40, screen.width(), 40)
        self.taskbar.setStyleSheet("background-color: rgba(0, 0, 0, 150); color: white;")
        self.taskbar.setText(f"Usuário: {self.username} | VirtualOS")
        
        # Mostrar desktop
        self.showMaximized()