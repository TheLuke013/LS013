from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QSizePolicy
from PySide6.QtCore import Qt, QTimer, QDateTime, QLocale, Signal
from PySide6.QtGui import QFont, QPainter, QLinearGradient, QColor, QBrush, QMouseEvent

from system.ui.desktop.start_menu import StartMenu

class Taskbar(QWidget):
    start_menu_created = Signal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.start_menu = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(20)

        self.start_button = QLabel("Iniciar")
        self.start_button.setStyleSheet("""
            QLabel {
                padding: 5px 10px;
                color: white;
                background: none;
                border-radius: 4px;
            }
            QLabel:hover {
                background-color: rgba(100, 100, 100, 180);
            }
        """)
        self.start_button.mousePressEvent = self.toggle_start_menu
        layout.addWidget(self.start_button)

        layout.addStretch()

        self.notification_area = QWidget()
        notification_layout = QHBoxLayout(self.notification_area)
        notification_layout.setContentsMargins(0, 0, 0, 0)
        notification_layout.setSpacing(15)

        self.clock_label = QLabel()
        self.clock_label.setFont(QFont("Segoe UI", 9))
        self.clock_label.setStyleSheet("color: white; background: none;")

        self.date_label = QLabel()
        self.date_label.setFont(QFont("Segoe UI", 9))
        self.date_label.setStyleSheet("color: white; background: none;")

        notification_layout.addWidget(self.clock_label)
        notification_layout.addWidget(self.date_label)

        layout.addWidget(self.notification_area)

        self.update_time()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        
    def toggle_start_menu(self, event: QMouseEvent):
        if not self.start_menu:
            self.start_menu = StartMenu(self.parent())
            self.start_menu_created.emit(self.start_menu)
        
        if self.start_menu.isVisible():
            self.start_menu.hide()
        else:
            self.position_start_menu()
            self.start_menu.show()
    
    def position_start_menu(self):
        if self.start_menu:
            pos = self.mapToGlobal(self.start_button.pos())
            pos.setY(pos.y() - self.start_menu.height() + 10)
            self.start_menu.move(pos)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor(50, 50, 50, 230))  #top
        gradient.setColorAt(1.0, QColor(30, 30, 30, 220))  #base

        painter.fillRect(self.rect(), QBrush(gradient))

        #top edge
        painter.setPen(QColor(255, 255, 255, 40))
        painter.drawLine(0, 0, self.width(), 0)

        super().paintEvent(event)

    def update_time(self):
        current_time = QDateTime.currentDateTime()

        self.clock_label.setText(current_time.toString("HH:mm"))

        locale = QLocale.system()
        formatted_date = locale.toString(current_time.date(), QLocale.LongFormat)
    
        self.date_label.setText(formatted_date)