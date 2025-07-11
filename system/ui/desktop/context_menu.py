from PySide6.QtWidgets import QMenu, QProxyStyle, QStyle
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QEvent
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, QLinearGradient, QAction

class MenuStyle(QProxyStyle):
    def styleHint(self, hint, option=None, widget=None, returnData=None):
        if hint == QStyle.SH_Menu_MouseTracking:
            return 1
        return super().styleHint(hint, option, widget, returnData)

class ContextMenu(QMenu):
    wallpaper_change_requested = Signal()
    create_folder_requested = Signal()
    refresh_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumWidth(200)
        
        self.setStyle(MenuStyle())
        self._setup_hover_style()
        
        self.hover_animation = QPropertyAnimation(self, b"")
        self.hover_animation.setDuration(150)
        self.hover_animation.setEasingCurve(QEasingCurve.OutQuad)
        
        self.current_hover_item = None
        
        self._create_actions()

    def _create_actions(self):
        try:
            self.wallpaper_action = QAction("Trocar Papel de Parede", self)
            self.wallpaper_action.triggered.connect(self.wallpaper_change_requested.emit)
            self.addAction(self.wallpaper_action)
            
            self.folder_action = QAction("Nova Pasta", self)
            self.folder_action.triggered.connect(self.create_folder_requested.emit)
            self.addAction(self.folder_action)
            
            self.addSeparator()
            
            self.refresh_action = QAction("Atualizar", self)
            self.refresh_action.triggered.connect(self.refresh_requested.emit)
            self.addAction(self.refresh_action)
        except Exception as e:
            print(f"Erro ao criar ações: {e}")

    def _setup_hover_style(self):
        self.setStyleSheet("""
            QMenu {
                background-color: rgba(50, 50, 50, 230);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 5px 0;
                color: #ffffff;
            }
            
            QMenu::item {
                padding: 8px 25px 8px 15px;
                margin: 2px 5px;
                border-radius: 4px;
                background-color: transparent;
                border: 1px solid transparent;
            }
            
            QMenu::item:selected {
                background-color: rgba(100, 100, 100, 180);
                border: 1px solid rgba(255, 255, 255, 0.15);
            }
            
            QMenu::item:hover {
                background-color: rgba(80, 80, 80, 180);
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            QMenu::item:pressed {
                background-color: rgba(70, 70, 70, 200);
            }
            
            QMenu::item:disabled {
                color: #777777;
            }
            
            QMenu::separator {
                height: 1px;
                background: rgba(255, 255, 255, 0.1);
                margin: 5px 10px;
            }
        """)

    def paintEvent(self, event):
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            bg_color = QColor(50, 50, 50, 230)
            painter.setBrush(QBrush(bg_color))
            painter.setPen(QPen(QColor(255, 255, 255, 30), 1))
            painter.drawRoundedRect(self.rect().adjusted(0, 0, -1, -1), 8, 8)
            
            super().paintEvent(event)
        except Exception as e:
            print(f"Erro no paintEvent: {e}")

    def event(self, event):
        try:
            if event.type() == QEvent.HoverMove:
                self.current_hover_item = self.actionAt(event.pos())
                self.update()
            return super().event(event)
        except Exception as e:
            print(f"Erro no event handler: {e}")
            return False

    def add_custom_action(self, text, icon=None, callback=None, shortcut=None):
        try:
            action = QAction(text, self)
            if icon:
                action.setIcon(icon)
            if callback:
                action.triggered.connect(callback)
            if shortcut:
                action.setShortcut(shortcut)
            self.addAction(action)
            return action
        except Exception as e:
            print(f"Erro ao adicionar ação customizada: {e}")
            return None