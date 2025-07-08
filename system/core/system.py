from PySide6.QtWidgets import QApplication, QLabel, QMainWindow
from PySide6.QtCore import Qt
from PySide6.QtCore import QObject, Signal
import sys
import os

from core.system_main_window import SystemMainWindow, WindowMode
from . import constants as CONSTS
from .log import *
from core.wallpaper import Wallpaper
from ui.splash_screen import SplashScreen
from ui.login_screen import LoginScreen

class LSystem013(QObject):
    def __init__(self):
        #configure "low-level system"
        os.chdir(CONSTS.ROOT_PATH)

        #init logger
        Log.init()
        LOG_INFO("Initializing virtual system {} in: {}", CONSTS.SYSTEM_NAME, os.getcwd())

        self.main_window = SystemMainWindow()
        self.main_window.show(WindowMode.MAXIMIZED)

        #show system splash screen
        self.show_splash_screen()
    
    def show_splash_screen(self):
        self.splash = SplashScreen()
        self.main_window.setCentralWidget(self.splash)
        self.splash.finished.connect(self.starting_system)
        self.splash.show()
    
    def starting_system(self):
        self.main_window.close()

        d_wp_path = os.path.abspath(os.path.join(CONSTS.DEFAULT_WALLPAPER_FILENAME))
        self.main_window.set_wallpaper(d_wp_path)

        self.main_window.show(WindowMode.MAXIMIZED)
        

        #show login screen
        self.login = LoginScreen()
        self.main_window.setCentralWidget(self.login)
        #self.login.login_success.connect(self.show_desktop)
        self.login.show()