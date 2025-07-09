from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, Signal
import os

from core.system_main_window import SystemMainWindow, WindowMode
from core.flags import SystemFlags
from . import constants as CONSTS
from .log import *
from ui.splash_screen import SplashScreen
from ui.login_screen import LoginScreen
from ui.shutdown_screen import ShutdownScreen
from ui.desktop import Desktop
from core.users_manager import UsersManager

class LSystem013(QObject):
    def __init__(self, flags: SystemFlags):
        #configure "low-level system"
        self.flags = flags

        self.window_mode = WindowMode.MAXIMIZED
        if SystemFlags.WINDOW_FULLSCREEN in self.flags:
            self.window_mode = WindowMode.FULLSCREEN
        
        os.chdir(CONSTS.ROOT_PATH)

        #init logger
        Log.init()
        LOG_INFO("Initializing virtual system {} in: {}", CONSTS.SYSTEM_NAME, os.getcwd())

        self.users_manager = UsersManager()

        self.main_window = SystemMainWindow()
        self.main_window.set_wallpaper(CONSTS.DEFAULT_WALLPAPER_FILENAME)
        self.main_window.show(self.window_mode)

        #show system splash screen
        if SystemFlags.SKIP_SPLASH_SCREEN in self.flags:
            self.starting_system()
        else:
            self.show_splash_screen()
    
    def show_splash_screen(self):
        self.main_window.hide_wallpaper()
        self.splash = SplashScreen()
        self.splash.setFixedSize(self.main_window.size())
        self.main_window.setCentralWidget(self.splash)
        self.splash.finished.connect(self.starting_system)
        self.splash.show()
    
    def show_desktop(self, username):
        self.desktop = Desktop(username)
        self.main_window.setCentralWidget(self.desktop)
        self.desktop.show()

    def shutdown_system(self):
        if SystemFlags.SKIP_SHUTDOWN_SCREEN in self.flags:
            QApplication.quit()
        else:
            self.main_window.hide_wallpaper()

            #delete login screen if is active
            if self.login:
                self.login.setParent(None)
                self.login.deleteLater()
                self.login = None

        
            self.shutdown_ui = ShutdownScreen()
            self.main_window.setCentralWidget(self.shutdown_ui)
            self.shutdown_ui.show()
            self.shutdown_ui.finished.connect(QApplication.quit)
    
    def starting_system(self):
        self.main_window.show_wallpaper()
        
        #show login screen
        self.login = LoginScreen()
        self.login.request_shutdown.connect(self.shutdown_system)
        self.main_window.setCentralWidget(self.login)
        self.login.login_success.connect(self.show_desktop)
        self.login.show()