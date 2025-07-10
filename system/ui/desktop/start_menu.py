from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFrame, QMessageBox
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, Signal, QSize
from PySide6.QtGui import QColor, QBrush, QLinearGradient, QPainter, QIcon

from core.constants import *

class StartMenu(QFrame):
    request_shutdown = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent, Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedWidth(400)
        self.setMinimumHeight(500)
        self.setMaximumHeight(600)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        self.setStyleSheet("""
            StartMenu {
                background-color: rgba(50, 50, 50, 230);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 10px;
            }
        """)
        
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
        layout.addWidget(user_frame)
        
        menu_buttons = [
            ("Programas", APPS_ICON),
            ("Documentos", DOCUMENT_ICON),
            ("Configurações", CONFIG_ICON),
            ("Desligar", POWER_ICON)
        ]
        
        for text, icon_path in menu_buttons:
            btn = QPushButton(text)
            
            if icon_path:
                btn.setIcon(QIcon(icon_path))
                btn.setIconSize(QSize(24, 24))
            
            btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(70, 70, 70, 150);
                    color: white;
                    border: none;
                    padding: 12px 15px 12px 45px;  /* Aumenta padding esquerdo para ícones */
                    text-align: left;
                    font-size: 12pt;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: rgba(100, 100, 100, 200);
                }
                QPushButton::icon {
                    left: 15px;  /* Posiciona o ícone à esquerda */
                }
            """)
            layout.addWidget(btn)
            
            if text == "Desligar":
                btn.clicked.connect(self.shutdown)
        
        layout.addStretch()
        
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.OutQuad)
    
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