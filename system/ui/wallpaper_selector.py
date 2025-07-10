from PySide6.QtWidgets import QWidget, QListWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QListWidgetItem
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QIcon

import os
from core.constants import *

class WallpaperSelector(QWidget):
    wallpaper_selected = Signal(str)
    
    def __init__(self, current_wallpaper):
        super().__init__()
        self.setWindowTitle("Selecionar Papel de Parede")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.wallpaper_list = QListWidget()
        self.wallpaper_list.setIconSize(QSize(200, 150))
        self.wallpaper_list.setViewMode(QListWidget.IconMode)
        self.wallpaper_list.setResizeMode(QListWidget.Adjust)
        self.wallpaper_list.setSpacing(10)
        
        self.load_wallpapers(WALLPAPERS_PATH)
        
        layout.addWidget(QLabel("Selecione um papel de parede:"))
        layout.addWidget(self.wallpaper_list)
        
        button_layout = QHBoxLayout()
        select_button = QPushButton("Selecionar")
        select_button.clicked.connect(self.select_wallpaper)
        
        cancel_button = QPushButton("Cancelar")
        cancel_button.clicked.connect(self.close)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(select_button)
        
        layout.addLayout(button_layout)
        
        self.setStyleSheet("""
            QListWidget::item {
                border: 1px solid #444;
                border-radius: 4px;
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #2a82da;
                border: 2px solid #1a62ba;
            }
        """)
    
    def load_wallpapers(self, directory):
        """Carrega todos os wallpapers do diret√≥rio especificado"""
        for filename in os.listdir(directory):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                full_path = os.path.join(directory, filename)
                
                pixmap = QPixmap(full_path)
                if not pixmap.isNull():
                    pixmap = pixmap.scaled(200, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    icon = QIcon(pixmap)
                    
                    item = QListWidgetItem(icon, filename)
                    item.setData(Qt.UserRole, full_path)
                    self.wallpaper_list.addItem(item)
    
    def select_wallpaper(self):
        """Emite o wallpaper selecionado"""
        selected_items = self.wallpaper_list.selectedItems()
        if selected_items:
            wallpaper_path = selected_items[0].data(Qt.UserRole)
            self.wallpaper_selected.emit(wallpaper_path)
            self.close()