from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QMovie

from system.core.constants import *

class ShutdownScreen(QWidget):
    finished = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(30)

        self.label = QLabel("Desligando...")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 36px; color: white;")

        self.loading = QLabel()
        self.loading.setAlignment(Qt.AlignCenter)
        self.movie = QMovie(LOADING_SPINNER_ICON)
        self.loading.setMovie(self.movie)
        self.movie.start()

        layout.addWidget(self.label)
        layout.addWidget(self.loading)

        self.timer = QTimer()
        self.timer.timeout.connect(self.quit_system)
        self.timer.start(3000)

    def quit_system(self):
        self.timer.stop()
        self.finished.emit()
        self.close()
