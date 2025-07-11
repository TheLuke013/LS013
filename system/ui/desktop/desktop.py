from PySide6.QtWidgets import (QLabel, QSizePolicy, QWidget, QVBoxLayout, QMenu, 
                              QHBoxLayout, QSpacerItem, QSizePolicy, QMessageBox, QMainWindow)
from PySide6.QtCore import Qt, Signal, QTimer, QDateTime
from PySide6.QtGui import QAction, QFont
import importlib

from system.core.constants import *
from system.core.log import *
from system.ui.wallpaper import Wallpaper
from system.ui.wallpaper_selector import WallpaperSelector
from system.ui.desktop.taskbar import Taskbar
from system.ui.desktop.start_menu import StartMenu
from system.ui.desktop.context_menu import ContextMenu
from system.core.apps_manager import AppsManager

class Desktop(QWidget):
    wallpaper_change_requested = Signal(str)
    
    def __init__(self, username, system):
        super().__init__()
        self.username = username
        self.system = system
        self.main_window = self.system.main_window
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
             
        self.main_window.change_wallpaper(DEFAULT_DESKTOP_WALLPAPER_FILENAME)
            
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)     
        
        self.desktop_area = QWidget()
        self.desktop_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout.addWidget(self.desktop_area)
        
        #taskbar
        self.taskbar = Taskbar(self)
        self.layout.addWidget(self.taskbar)
        self.taskbar.start_menu_created.connect(
            lambda menu: menu.request_shutdown.connect(self.system.request_shutdown)
        )
        self.taskbar.start_menu_created.connect(self.connect_start_menu_signals)
        
        self.start_menu = StartMenu(self)
        self.start_menu.hide()
        
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    def connect_shutdown_signal(self, start_menu):
        start_menu.request_shutdown.connect(self.handle_shutdown)
    
    def show_context_menu(self, pos):
        menu = ContextMenu(self)
        menu.setFont(QFont("Segoe UI", 10))
        
        menu.wallpaper_change_requested.connect(self.open_wallpaper_selector)
        menu.create_folder_requested.connect(self.create_new_folder)
        menu.refresh_requested.connect(self.refresh_desktop)
        
        menu.add_custom_action("Abrir Terminal", callback=self.open_terminal)
        
        menu.exec_(self.mapToGlobal(pos))
    
    def connect_start_menu_signals(self, start_menu):
        """Conecta todos os sinais do menu iniciar"""
        start_menu.request_shutdown.connect(self.system.request_shutdown)
        start_menu.open_app.connect(self.launch_application)
    
    def launch_application(self, app_id: str):
        try:
            from system.core.apps_manager import AppsManager
            import importlib.util
            from pathlib import Path

            manager = AppsManager()
            app = manager.get_app(app_id)
            
            module_path = Path(ROOT_PATH) / f"{app.manifest.package.replace('.', '/')}.py"
            
            spec = importlib.util.spec_from_file_location(
                app.manifest.package,
                str(module_path)
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if hasattr(module, 'create_app_instance'):
                app_instance = module.create_app_instance(parent=self)
            else:
                app_class = getattr(module, app.manifest.main_class)
                app_instance = app_class(parent=self)

            if not app_instance:
                raise RuntimeError("Instância do aplicativo não foi criada")

            if isinstance(app_instance, QMainWindow):
                app_instance.setWindowFlags(
                    Qt.Window | 
                    Qt.WindowCloseButtonHint |
                    Qt.WindowMinimizeButtonHint |
                    Qt.WindowMaximizeButtonHint
                )
                app_instance.setWindowModality(Qt.NonModal)
                
            app_instance.show()
            app_instance.raise_()
            app_instance.activateWindow()

        except Exception as e:
            LOG_ERROR(f"Falha ao iniciar app {app_id}: {str(e)}")
            QMessageBox.critical(self, "Erro", f"Não foi possível iniciar o aplicativo.\nErro: {str(e)}")
            
    def create_new_folder(self):
        LOG_WARN("Implement method: create_new_folder")
    
    def refresh_desktop(self):
        LOG_WARN("Implement method: refresh_desktop")
    
    def open_terminal(self):
        LOG_WARN("Implement method: open_terminal")
    
    def open_wallpaper_selector(self):
        self.wallpaper_selector = WallpaperSelector("")
        self.wallpaper_selector.wallpaper_selected.connect(self.change_wallpaper_requested)
        self.wallpaper_selector.show()
    
    def change_wallpaper_requested(self, new_wallpaper_path):
        self.wallpaper_change_requested.emit(new_wallpaper_path)