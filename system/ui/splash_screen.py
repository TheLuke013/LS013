from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QProgressBar, QSizePolicy
from PySide6.QtCore import Qt, QTimer, Signal

class SplashScreen(QWidget):
    finished = Signal()
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAutoFillBackground(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignCenter)

        self.logo = QLabel("LSystem 013")
        self.logo.setAlignment(Qt.AlignCenter)
        self.logo.setStyleSheet("font-size: 48px; color: white;")
        layout.addWidget(self.logo)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setFixedWidth(300)

        progress_layout = QHBoxLayout()
        progress_layout.addStretch()
        progress_layout.addWidget(self.progress)
        progress_layout.addStretch()
        layout.addLayout(progress_layout)

        self.load_progress = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(30)
    
    def update_progress(self):
        self.load_progress += 1
        self.progress.setValue(self.load_progress)
        
        if self.load_progress >= 100:
            self.timer.stop()
            self.finished.emit()
            self.close()