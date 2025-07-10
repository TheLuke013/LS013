from PySide6.QtWidgets import (QWidget, QListWidget, QVBoxLayout, QHBoxLayout, 
                              QPushButton, QLabel, QListWidgetItem, QProgressBar)
from PySide6.QtCore import Qt, Signal, QSize, QThread, QMutex, QWaitCondition
from PySide6.QtGui import QPixmap, QIcon, QImage, QPainter
import os
import time
from core.constants import *

class ThumbnailGenerator(QThread):
    progress_updated = Signal(int, int)
    thumbnail_generated = Signal(str, QPixmap) 

    def __init__(self, directory):
        super().__init__()
        self.directory = directory
        self.mutex = QMutex()
        self.condition = QWaitCondition()
        self.restart = False
        self.abort = False

    def run(self):
        files = [f for f in os.listdir(self.directory) 
                if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        total = len(files)
        
        for idx, filename in enumerate(files):
            self.mutex.lock()
            if self.abort:
                self.mutex.unlock()
                return
            self.mutex.unlock()
            
            full_path = os.path.join(self.directory, filename)
            
            img = QImage(full_path)
            if img.isNull():
                continue
                
            thumbnail = img.scaled(200, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            pixmap = QPixmap.fromImage(thumbnail)
            
            self.thumbnail_generated.emit(full_path, pixmap)
            self.progress_updated.emit(idx + 1, total)
            
            time.sleep(0.02)
            
            self.mutex.lock()
            if self.restart:
                self.restart = False
                self.mutex.unlock()
                break
            self.mutex.unlock()

    def stop(self):
        self.mutex.lock()
        self.abort = True
        self.condition.wakeAll()
        self.mutex.unlock()
        self.wait(2000)

class WallpaperSelector(QWidget):
    wallpaper_selected = Signal(str)
    
    def __init__(self, current_wallpaper):
        super().__init__()
        self.setWindowTitle("Selecionar Papel de Parede")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.wallpaper_list = QListWidget()
        self.wallpaper_list.setIconSize(QSize(200, 150))
        self.wallpaper_list.setViewMode(QListWidget.IconMode)
        self.wallpaper_list.setResizeMode(QListWidget.Adjust)
        self.wallpaper_list.setSpacing(10)
        self.wallpaper_list.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        layout.addWidget(self.wallpaper_list)
        
        button_layout = QHBoxLayout()
        self.select_button = QPushButton("Selecionar")
        self.select_button.setEnabled(False)
        self.select_button.clicked.connect(self.select_wallpaper)
        
        cancel_button = QPushButton("Cancelar")
        cancel_button.clicked.connect(self.close)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(self.select_button)
        
        layout.addLayout(button_layout)
        
        self.thumbnail_thread = ThumbnailGenerator(WALLPAPERS_PATH)
        self.thumbnail_thread.thumbnail_generated.connect(self.add_thumbnail_item)
        self.thumbnail_thread.progress_updated.connect(self.update_progress)
        self.thumbnail_thread.finished.connect(self.loading_finished)
        
        self.start_loading()
        
        self.setStyleSheet("""
            QListWidget::item {
                border: 1px solid #444;
                border-radius: 4px;
                padding: 5px;
                background-color: #2a2a2a;
            }
            QListWidget::item:selected {
                background-color: #2a82da;
                border: 2px solid #1a62ba;
            }
            QProgressBar {
                border: 1px solid #444;
                border-radius: 3px;
                text-align: center;
                background: #2a2a2a;
            }
            QProgressBar::chunk {
                background-color: #2a82da;
                width: 10px;
            }
        """)
    
    def start_loading(self):
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.wallpaper_list.clear()
        self.select_button.setEnabled(False)
        self.thumbnail_thread.start()
    
    def update_progress(self, current, total):
        percent = int((current / total) * 100) if total > 0 else 0
        self.progress_bar.setValue(percent)
        self.progress_bar.setFormat(f"Carregando: {percent}% ({current}/{total})")
    
    def add_thumbnail_item(self, file_path, pixmap):
        filename = os.path.basename(file_path)
        icon = QIcon(pixmap)
        
        item = QListWidgetItem(icon, filename)
        item.setData(Qt.UserRole, file_path)
        self.wallpaper_list.addItem(item)
    
    def loading_finished(self):
        self.progress_bar.setVisible(False)
        self.select_button.setEnabled(True)
        
        if self.wallpaper_list.count() > 0:
            self.wallpaper_list.setCurrentRow(0)
    
    def select_wallpaper(self):
        selected_items = self.wallpaper_list.selectedItems()
        if selected_items:
            wallpaper_path = selected_items[0].data(Qt.UserRole)
            self.wallpaper_selected.emit(wallpaper_path)
            self.close()
    
    def closeEvent(self, event):
        if self.thumbnail_thread.isRunning():
            self.thumbnail_thread.stop()
        super().closeEvent(event)