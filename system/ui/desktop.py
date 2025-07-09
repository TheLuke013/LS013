from PySide6.QtWidgets import QLabel, QSizePolicy, QWidget
from PySide6.QtCore import Qt

from core.constants import *

class Desktop(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.taskbar = QLabel(self)
        self.taskbar.setGeometry(0, self.height() - 40, self.width(), 40)
        self.taskbar.setStyleSheet("background-color: rgba(0, 0, 0, 150); color: white;")
        self.taskbar.setText(f"Usuário: {self.username} | LSystem 013")