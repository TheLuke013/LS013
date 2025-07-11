import platform
import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QTreeView, QSplitter, QFileSystemModel,
                              QStyle)
from PySide6.QtCore import QDir, Qt
from PySide6.QtGui import QAction
from api.application import Application

class SystemApp(Application):
    def __init__(self, parent=None):
        super().__init__("System Info", 800, 600, parent)
        self.setWindowIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        
    def setup_ui(self):
        main_layout = QVBoxLayout()
        self.central_widget = QWidget()
        self.central_widget.setLayout(main_layout)
        self.setCentralWidget(self.central_widget)

        # Área de informações do sistema
        info_layout = QVBoxLayout()
        
        # Informações básicas sem psutil
        info_layout.addWidget(QLabel(f"<b>Sistema Virtual:</b> {platform.system()} {platform.release()}"))
        info_layout.addWidget(QLabel(f"<b>Arquitetura:</b> {platform.architecture()[0]}"))
        info_layout.addWidget(QLabel(f"<b>Processador:</b> {platform.processor() or 'Não detectado'}"))
        
        # Espaço para futuras expansões
        info_layout.addWidget(QLabel("\n<b>Dispositivos:</b>"))
        
        # Lista de unidades de disco (alternativa sem psutil)
        drives = []
        if os.name == 'nt':  # Windows
            drives = [f"{d}:\\" for d in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' if os.path.exists(f"{d}:\\")]
        else:  # Linux/Mac
            drives = ["/"]  # Mostra apenas a raiz
            
        for drive in drives:
            info_layout.addWidget(QLabel(f"• {drive}"))
        
        main_layout.addLayout(info_layout)
        self.statusBar().showMessage("Sistema pronto")
    
    def create_actions(self):
        """Ações básicas do menu"""
        refresh_action = QAction("Atualizar", self)
        refresh_action.triggered.connect(self.update_info)
        
        menu = self.menuBar().addMenu("Sistema")
        menu.addAction(refresh_action)
    
    def update_info(self):
        """Atualiza as informações exibidas"""
        self.statusBar().showMessage("Informações atualizadas", 2000)