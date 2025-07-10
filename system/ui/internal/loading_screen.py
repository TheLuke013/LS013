from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QSizePolicy
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QMovie

from core.constants import *

class LoadingScreen(QWidget):
    def __init__(self, message="Carregando..."):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.label = QLabel(message)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("""
            font-size: 24px;
            color: white;
            background-color: transparent;
        """)
        
        self.loading = QLabel()
        self.loading.setStyleSheet("background-color: transparent")
        self.loading.setAlignment(Qt.AlignCenter)
        self.loading.setFixedSize(64, 64)
        
        self.movie = QMovie(LOADING_SPINNER_ICON)
        self.loading.setMovie(self.movie)
        self.movie.setScaledSize(QSize(64, 64))
        self.movie.start()
        
        layout.addWidget(self.label)
        layout.addWidget(self.loading)
        
        self.setStyleSheet("""
            background-color: rgba(0, 0, 0, 180);
        """)