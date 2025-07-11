from PySide6.QtWidgets import QMainWindow
from PySide6.QtCore import Qt
from abc import abstractmethod

class Application(QMainWindow):
    def __init__(self, title: str, width: int, height: int, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle(title)
        self.resize(width, height)
        
        self.setWindowFlags(
            self.windowFlags() | 
            Qt.Window |
            Qt.WindowCloseButtonHint |
            Qt.WindowMinimizeButtonHint |
            Qt.WindowMaximizeButtonHint
        )
        
        self.desktop_parent = parent
        
        #default style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #252526;
                color: #D4D4D4;
            }
            QDockWidget {
                background: #1E1E1E;
                border: 1px solid #3F3F46;
            }
            QDockWidget::title {
                background: #252526;
                padding: 5px;
                text-align: left;
            }
        """)
        
        self.setup_ui()
    
    def showEvent(self, event):
        super().showEvent(event)
        
        if self.desktop_parent and hasattr(self.desktop_parent, 'available_rect'):
            available_rect = self.desktop_parent.available_rect
            
            current_size = self.size()
            new_width = min(current_size.width(), available_rect.width())
            new_height = min(current_size.height(), available_rect.height())
            
            self.resize(new_width, new_height)
            
            center_point = available_rect.center()
            frame_geo = self.frameGeometry()
            frame_geo.moveCenter(center_point)
            self.move(frame_geo.topLeft())
        
        self.raise_()
        self.activateWindow()
    
    @abstractmethod
    def setup_ui(self):
        pass
   