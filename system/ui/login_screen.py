from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QSizePolicy
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QMessageBox

from core.auth import Auth

class LoginScreen(QWidget):
    login_success = Signal(str)
    request_shutdown = Signal()
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        self.logo = QLabel("LSystem 013")
        self.logo.setAlignment(Qt.AlignCenter)
        self.logo.setStyleSheet("font-size: 48px; color: white; margin-top: 200px; margin-bottom: 100px; background-color: transparent;")
        
        form_layout = QVBoxLayout()
        form_layout.setAlignment(Qt.AlignCenter)
        form_layout.setSpacing(20)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Usuário")
        self.username_input.setFixedWidth(300)
        self.username_input.setFixedHeight(40)
        self.username_input.textChanged.connect(self.validate_inputs)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Senha")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedWidth(300)
        self.password_input.setFixedHeight(40)
        self.password_input.textChanged.connect(self.validate_inputs)
        
        self.login_button = QPushButton("Entrar")
        self.login_button.setFixedWidth(300)
        self.login_button.setFixedHeight(50)
        self.login_button.clicked.connect(self.attempt_login)
        self.login_button.setEnabled(False)
        
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(self.login_button)
        
        footer = QHBoxLayout()
        power_button = QPushButton("⏻")
        power_button.setFixedSize(50, 50)
        power_button.clicked.connect(self.shutdown)
        
        footer.addStretch()
        footer.addWidget(power_button)
        
        main_layout.addWidget(self.logo)
        main_layout.addLayout(form_layout)
        main_layout.addStretch()
        main_layout.addLayout(footer)
        
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 180);
            }
            QLineEdit {
                background-color: rgba(255, 255, 255, 30);
                border: 1px solid rgba(255, 255, 255, 100);
                border-radius: 5px;
                color: white;
                font-size: 16px;
                padding: 5px;
            }
            QPushButton {
                background-color: rgba(0, 100, 200, 200);
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: rgba(0, 120, 230, 220);
            }
        """)
    
    def validate_inputs(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if username and password:
            self.login_button.setEnabled(True)
        else:
            self.login_button.setEnabled(False)
    
    def attempt_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Campos Vazios", "Por favor, preencha todos os campos.")
            return

        auth = Auth()
        
        if auth.authenticate_user(username, password):
            self.login_success.emit(username)
            self.close()
        else:
            QMessageBox.warning(self, "Usuario invalido", "Usuario ou senha estão incorretos")
            self.password_input.clear()
    
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