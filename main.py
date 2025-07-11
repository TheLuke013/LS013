from PySide6.QtWidgets import QApplication
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from system.core.system import LSystem013 
from system.core.flags import SystemFlags

if __name__ == "__main__":
    flags = SystemFlags.NONE
    
    if len(sys.argv) > 1:
        if "-fullscreen" in sys.argv:
            flags |= SystemFlags.WINDOW_FULLSCREEN
            print("'-fullscreen' argument | Ficar em tela cheia")
        
        if "-skipsplash" in sys.argv:
            flags |= SystemFlags.SKIP_SPLASH_SCREEN 
            print("'-skipsplash' argument | Pular tela de splash")
        
        if "-skipshutdown" in sys.argv:
            flags |= SystemFlags.SKIP_SHUTDOWN_SCREEN
            print("'-skipshutdown' argument | Pular tela de desligamento")
        
        if "-skiplogin" in sys.argv:
            flags |= SystemFlags.SKIP_LOGIN_SCREEN
            print("'-skiplogin' argument | Pular tela de login")
    else:
        print("Nenhum argumento extra foi passado")

    app = QApplication(sys.argv)
    ls013 = LSystem013(flags)
    app.exec()