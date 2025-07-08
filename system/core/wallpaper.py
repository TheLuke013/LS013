import os
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel

from log import *

class Wallpaper(QLabel):
    def __init__(self, wp_path, parent=None):
        super().__init__(parent)

        if not os.path.exists(wp_path):
            LOG_ERROR("Wallpaper not found in path: {}", wp_path)
            raise FileNotFoundError(f"Wallpaper not found: {wp_path}")

        self.original_pixmap = QPixmap(wp_path)
        if self.original_pixmap.isNull():
            LOG_ERROR("QPixmap failed to load wallpaper image")
            raise ValueError("Failed to load image with QPixmap")

        self.setAlignment(Qt.AlignCenter)
        self.setScaledContents(False)

        self.update_wallpaper(parent.width(), parent.height())

    def update_wallpaper(self, width, height):
        if not self.original_pixmap.isNull():
            scaled = self.original_pixmap.scaled(
                width, height,
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )
            self.setPixmap(scaled)
            self.setGeometry(0, 0, width, height)
