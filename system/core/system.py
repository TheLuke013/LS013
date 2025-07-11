from PySide6.QtWidgets import QApplication, QGraphicsOpacityEffect
from PySide6.QtCore import QObject, Signal, QPropertyAnimation, QEasingCurve, QTimer, QPoint, QParallelAnimationGroup
from PySide6.QtGui import QColor, QPainter
import os

from system.core.system_main_window import SystemMainWindow, WindowMode
from system.core.flags import SystemFlags
from . import constants as CONSTS
from .log import *
from system.ui.internal.splash_screen import SplashScreen
from system.ui.internal.login_screen import LoginScreen
from system.ui.internal.shutdown_screen import ShutdownScreen
from system.ui.desktop.desktop import Desktop
from system.ui.internal.loading_screen import LoadingScreen
from system.core.users_manager import UsersManager, UserPrivilege
from system.core.apps_manager import AppsManager

class LSystem013(QObject):
    def __init__(self, flags: SystemFlags):
        #configure "low-level system"
        self.flags = flags
        self.login = None
        self.shutdown_ui = None
        self._active_widgets = []
        self.apps_manager = None

        self.window_mode = WindowMode.MAXIMIZED
        if SystemFlags.WINDOW_FULLSCREEN in self.flags:
            self.window_mode = WindowMode.FULLSCREEN
        
        os.chdir(CONSTS.ROOT_PATH)

        #init logger
        Log.init()
        LOG_INFO("Initializing virtual system {} in: {}", CONSTS.SYSTEM_NAME, os.getcwd())

        self.users_manager = UsersManager()
        self.users_manager.create_user("admin", "123", UserPrivilege.ADMIN)

        self.main_window = SystemMainWindow()
        self.main_window.set_wallpaper(CONSTS.DEFAULT_WALLPAPER_FILENAME)
        self.main_window.show(self.window_mode)

        #show system splash screen
        if SystemFlags.SKIP_SPLASH_SCREEN in self.flags:
            self.starting_system()
        else:
            self.show_splash_screen()
    
    def launch_application(self, app_id: str):
        """Método chamado quando um app é iniciado pelo menu"""
        manager = AppsManager()
        try:
            app = manager.get_app(app_id)
            success, message = AppLauncher.launch_app(app)
            
            if not success:
                self.show_error_message(message)
        except Exception as e:
            self.show_error_message(f"Erro crítico: {str(e)}")
            
    def _add_widget(self, widget):
        """Adiciona um widget à lista de controle"""
        self._active_widgets.append(widget)
        return widget

    def _cleanup_widgets(self):
        """Limpeza segura de todos os widgets"""
        for widget in self._active_widgets[:]:
            try:
                if widget and widget.parent() is None:
                    widget.deleteLater()
                self._active_widgets.remove(widget)
            except RuntimeError:
                self._active_widgets.remove(widget)
                continue
                
    def show_splash_screen(self):
        self.main_window.hide_wallpaper()
        self.splash = self._add_widget(SplashScreen())
        self.splash.setFixedSize(self.main_window.size())
        self.main_window.setCentralWidget(self.splash)
        self.splash.finished.connect(self.starting_system)
        self.splash.show()
    
    def show_desktop(self, username):
        self.loading = self._add_widget(LoadingScreen("Preparando o desktop..."))
        self.loading.setFixedSize(self.main_window.size())
        self.main_window.setCentralWidget(self.loading)
        self.loading.show()
        
        QTimer.singleShot(1500, lambda: self._finish_desktop_load(username))

    def _finish_desktop_load(self, username):
        self.desktop = Desktop(username, self)
        self.desktop.wallpaper_change_requested.connect(self.change_wallpaper)
        
        self.desktop.setFixedSize(self.main_window.size())   
        self.main_window.setCentralWidget(self.desktop)
        
        opacity_effect = QGraphicsOpacityEffect(self.desktop)
        self.desktop.setGraphicsEffect(opacity_effect)
        opacity_effect.setOpacity(1)
        
        self.desktop.show()
        
        self.loading.deleteLater()
    
    def change_wallpaper(self, new_wp_path):
        """Método para trocar o wallpaper"""
        if not hasattr(self, 'main_window') or not self.main_window:
            LOG_ERROR("Main window not available")
            return False
        
        QApplication.processEvents()
        
        success = self.main_window.change_wallpaper(new_wp_path)
        
        if success:
            LOG_INFO("Wallpaper changed successfully to: {}", new_wp_path)
            self.main_window.repaint()
            QApplication.processEvents()
        else:
            LOG_ERROR("Failed to change wallpaper to: {}", new_wp_path)
        
        return success
    
    def shutdown_system(self):
        if SystemFlags.SKIP_SHUTDOWN_SCREEN in self.flags:
            self._cleanup_widgets()
            QApplication.quit()
            return
        
        self.main_window.hide_wallpaper()
        self._cleanup_widgets()
        
        self.shutdown_ui = self._add_widget(ShutdownScreen())
        self.main_window.setCentralWidget(self.shutdown_ui)
        self.shutdown_ui.show()
        self.shutdown_ui.finished.connect(QApplication.quit)

    def request_shutdown(self):
        try:
            self.shutdown_system()
        except Exception as e:
            LOG_ERROR("Erro durante desligamento: {}", str(e))
            QApplication.quit()
            
    def load_applications(self):
        self.apps_manager = AppsManager()
             
    def starting_system(self):
        self.load_applications()
        
        if SystemFlags.SKIP_LOGIN_SCREEN in self.flags:
            self.show_desktop("developer")
        else:
            
            self.main_window.show_wallpaper()
        
            #show login screen
            self.login = self._add_widget(LoginScreen())
            self.login.request_shutdown.connect(self.shutdown_system)
            self.main_window.setCentralWidget(self.login)
            self.login.login_success.connect(self.show_desktop)
            self.login.show()