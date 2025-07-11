import platform
import psutil
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                              QProgressBar, QGroupBox, QGridLayout)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon

from api.application import Application
from system.core.constants import *

class SystemApp(Application):
    def __init__(self, parent=None):
        super().__init__("System Info", 600, 400, parent)
        self.setWindowIcon(QIcon(SYSTEM_ICON))
        self.setup_ui()
        self.update_info()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_info)
        self.timer.start(2000)
    
    def setup_ui(self):
        main_layout = QVBoxLayout()
        self.central_widget = QWidget()
        self.central_widget.setLayout(main_layout)
        self.setCentralWidget(self.central_widget)
        
        system_group = QGroupBox("Informações do Sistema")
        system_layout = QGridLayout()
        
        system_layout.addWidget(QLabel("Sistema Virtual:"), 0, 0)
        self.virtual_system_label = QLabel()
        system_layout.addWidget(self.virtual_system_label, 0, 1)
        
        system_layout.addWidget(QLabel("Versão do Sistema Virtual:"), 1, 0)
        self.virtual_version_label = QLabel()
        system_layout.addWidget(self.virtual_version_label, 1, 1)
        
        system_layout.addWidget(QLabel("Sistema Operacional Base:"), 2, 0)
        self.os_label = QLabel()
        system_layout.addWidget(self.os_label, 2, 1)
        
        system_layout.addWidget(QLabel("Arquitetura:"), 3, 0)
        self.arch_label = QLabel()
        system_layout.addWidget(self.arch_label, 3, 1)
        
        system_layout.addWidget(QLabel("Processador:"), 4, 0)
        self.cpu_model_label = QLabel()
        system_layout.addWidget(self.cpu_model_label, 4, 1)
        
        system_layout.addWidget(QLabel("Núcleos/Threads:"), 5, 0)
        self.cpu_cores_label = QLabel()
        system_layout.addWidget(self.cpu_cores_label, 5, 1)
        
        system_layout.addWidget(QLabel("Frequência:"), 6, 0)
        self.cpu_freq_label = QLabel()
        system_layout.addWidget(self.cpu_freq_label, 6, 1)
        
        system_layout.addWidget(QLabel("Uso da CPU:"), 7, 0)
        self.cpu_usage_bar = QProgressBar()
        system_layout.addWidget(self.cpu_usage_bar, 7, 1)
        
        system_layout.addWidget(QLabel("Temperatura:"), 8, 0)
        self.cpu_temp_label = QLabel("N/D")
        system_layout.addWidget(self.cpu_temp_label, 8, 1)
        
        system_group.setLayout(system_layout)
        main_layout.addWidget(system_group)
        
        mem_group = QGroupBox("Memória RAM")
        mem_layout = QGridLayout()
        
        mem_layout.addWidget(QLabel("Total:"), 0, 0)
        self.mem_total_label = QLabel()
        mem_layout.addWidget(self.mem_total_label, 0, 1)
        
        mem_layout.addWidget(QLabel("Usada:"), 1, 0)
        self.mem_used_label = QLabel()
        mem_layout.addWidget(self.mem_used_label, 1, 1)
        
        mem_layout.addWidget(QLabel("Disponível:"), 2, 0)
        self.mem_available_label = QLabel()
        mem_layout.addWidget(self.mem_available_label, 2, 1)
        
        self.mem_progress = QProgressBar()
        mem_layout.addWidget(self.mem_progress, 3, 0, 1, 2)
        
        mem_group.setLayout(mem_layout)
        main_layout.addWidget(mem_group)
        
        net_group = QGroupBox("Rede")
        net_layout = QVBoxLayout()
        
        self.net_label = QLabel("Verificando conexão...")
        net_layout.addWidget(self.net_label)
        
        net_group.setLayout(net_layout)
        main_layout.addWidget(net_group)
        
        main_layout.addStretch()
    
    def update_info(self):
        self.virtual_system_label.setText(f"{SYSTEM_NAME}")
        self.virtual_version_label.setText("Versão de protótipo")
        self.os_label.setText(f"{platform.system()} {platform.release()}")
        self.arch_label.setText(platform.architecture()[0])
        
        cpu_info = platform.processor() or "Não detectado"
        if cpu_info == "":
            cpu_info = psutil.cpu_info()[0].model
        self.cpu_model_label.setText(cpu_info.split('@')[0].strip())
        
        cores = psutil.cpu_count(logical=False)
        threads = psutil.cpu_count(logical=True)
        self.cpu_cores_label.setText(f"{cores} núcleos, {threads} threads")
        
        freq = psutil.cpu_freq()
        self.cpu_freq_label.setText(f"{freq.current:.0f} MHz (max: {freq.max:.0f} MHz)")
        
        cpu_usage = psutil.cpu_percent()
        self.cpu_usage_bar.setValue(int(cpu_usage))
        self.cpu_usage_bar.setFormat(f"{cpu_usage:.1f}%")
        
        try:
            temps = psutil.sensors_temperatures()
            if 'coretemp' in temps:
                cpu_temp = temps['coretemp'][0].current
                self.cpu_temp_label.setText(f"{cpu_temp}°C")
        except:
            pass
        
        mem = psutil.virtual_memory()
        self.mem_total_label.setText(f"{mem.total/1024**3:.1f} GB")
        self.mem_used_label.setText(f"{mem.used/1024**3:.1f} GB")
        self.mem_available_label.setText(f"{mem.available/1024**3:.1f} GB")
        self.mem_progress.setValue(mem.percent)
        self.mem_progress.setFormat(f"{mem.percent}% usado")
        
        net_status = "Desconectado"
        net_stats = psutil.net_if_stats()
        for interface, stats in net_stats.items():
            if stats.isup:
                if "wi" in interface.lower() or "wlan" in interface.lower():
                    net_status = f"Conectado (Wi-Fi - {interface})"
                    break
                elif "eth" in interface.lower() or "ethernet" in interface.lower():
                    net_status = f"Conectado (Cabo - {interface})"
                    break
                else:
                    net_status = f"Conectado ({interface})"
        
        self.net_label.setText(f"Status: {net_status}")
    
    def create_actions(self):
        refresh_action = QAction("Atualizar Agora", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.update_info)
        
        exit_action = QAction("Sair", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        
        menu = self.menuBar().addMenu("Sistema")
        menu.addAction(refresh_action)
        menu.addAction(exit_action)