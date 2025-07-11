from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                             QPushButton, QFrame, QMessageBox, QScrollArea)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, Signal, QSize
from PySide6.QtGui import QColor, QBrush, QLinearGradient, QPainter, QIcon

from system.core.constants import *
from system.core.apps_manager import AppsManager
from system.core.app import App 

class StartMenu(QFrame):
    request_shutdown = Signal()
    open_app = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent, Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedWidth(400)
        self.setMinimumHeight(500)
        self.setMaximumHeight(600)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(10)
        
        self.setStyleSheet("""
            StartMenu {
                background-color: rgba(50, 50, 50, 230);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 10px;
            }
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                width: 6px;
                background: rgba(30, 30, 30, 150);
            }
            QScrollBar::handle:vertical {
                background: rgba(100, 100, 100, 200);
                min-height: 20px;
                border-radius: 3px;
            }
        """)
        
        self._setup_user_area()
        
        self._setup_main_menu()
        
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.OutQuad)
    
    def _setup_user_area(self):
        user_frame = QFrame()
        user_frame.setStyleSheet("""
            background-color: rgba(70, 70, 70, 150);
            border-radius: 8px;
            padding: 15px;
        """)
        user_layout = QVBoxLayout(user_frame)
        
        username = QLabel("Usuário")
        username.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        
        user_layout.addWidget(username)
        self.main_layout.addWidget(user_frame)
    
    def _setup_main_menu(self):
        self.programs_scroll = QScrollArea()
        self.programs_scroll.setWidgetResizable(True)
        self.programs_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.programs_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        self.programs_container = QFrame()
        self.programs_container.setLayout(QVBoxLayout())
        self.programs_container.layout().setContentsMargins(5, 5, 5, 5)
        self.programs_container.layout().setSpacing(5)
        self.programs_scroll.setWidget(self.programs_container)
        self.programs_scroll.setVisible(False)
        
        menu_buttons = [
            ("Programas", APPS_ICON, self.toggle_programs),
            ("Documentos", DOCUMENT_ICON, None),
            ("Configurações", CONFIG_ICON, None),
            ("Desligar", POWER_ICON, self.shutdown)
        ]
        
        for text, icon_path, callback in menu_buttons:
            btn = QPushButton(text)
            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(QSize(24, 24))
            
            btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(70, 70, 70, 150);
                    color: white;
                    border: none;
                    padding: 12px 15px 12px 45px;
                    text-align: left;
                    font-size: 12pt;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: rgba(100, 100, 100, 200);
                }
                QPushButton::icon {
                    left: 15px;
                }
            """)
            
            if callback:
                btn.clicked.connect(callback)
            
            self.main_layout.addWidget(btn)
        
        self.main_layout.addWidget(self.programs_scroll)
        self.main_layout.addStretch()
    
    def toggle_programs(self):
        if not self.programs_scroll.isVisible():
            self.load_applications()
        self.programs_scroll.setVisible(not self.programs_scroll.isVisible())
        
        self.adjustSize()
    
    def load_applications(self):
        for i in reversed(range(self.programs_container.layout().count())):
            widget = self.programs_container.layout().itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        manager = AppsManager()
        
        if not manager.apps:
            label = QLabel("Nenhum aplicativo instalado")
            label.setStyleSheet("color: rgba(255, 255, 255, 150); padding: 10px;")
            self.programs_container.layout().addWidget(label)
            return
        
        for app in manager.apps:
            btn = QPushButton(app.name)
            btn.setToolTip(app.manifest.description)
            
            if app.has_icon():
                btn.setIcon(QIcon(app.icon_path))
                btn.setIconSize(QSize(20, 20))
            
            btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(60, 60, 60, 180);
                    color: white;
                    border: none;
                    padding: 8px 15px 8px 40px;
                    text-align: left;
                    font-size: 11pt;
                    border-radius: 5px;
                    margin-left: 20px;
                    margin-right: 5px;
                }
                QPushButton:hover {
                    background-color: rgba(90, 90, 90, 200);
                }
                QPushButton::icon {
                    left: 10px;
                }
            """)
            
            btn.clicked.connect(lambda _, app_id=app.app_id: self.open_application(app_id))
            self.programs_container.layout().addWidget(btn)
    
    def open_application(self, app_id: str):
        self.open_app.emit(app_id)
        self.hide()
        
    def shutdown(self):
        confirm = QMessageBox.question(
            self,
            "Desligar o sistema",
            "Tem certeza que deseja desligar o sistema?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            self.request_shutdown.emit()
    
    def showEvent(self, event):
        taskbar = self.parent().taskbar
        start_button_pos = taskbar.start_button.mapToGlobal(QPoint(0, 0))
        
        start_pos = QPoint(start_button_pos.x(), start_button_pos.y() + 20)
        end_pos = QPoint(start_button_pos.x(), start_button_pos.y() - self.height() + 2)
        
        self.move(start_pos)
        self.animation.setStartValue(start_pos)
        self.animation.setEndValue(end_pos)
        self.animation.start()
        
        super().showEvent(event)
    
    def hide(self):
        taskbar = self.parent().taskbar
        start_button_pos = taskbar.start_button.mapToGlobal(QPoint(0, 0))
        
        self.animation.setStartValue(self.pos())
        self.animation.setEndValue(QPoint(start_button_pos.x(), start_button_pos.y() + 20))
        self.animation.finished.connect(super().hide)
        self.animation.start()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        #background gradient
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor(60, 60, 60, 240))
        gradient.setColorAt(1.0, QColor(40, 40, 40, 230))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 10, 10)
        
        #subtle edge
        painter.setPen(QColor(255, 255, 255, 30))
        painter.drawRoundedRect(self.rect().adjusted(0, 0, -1, -1), 10, 10)
        
        super().paintEvent(event)