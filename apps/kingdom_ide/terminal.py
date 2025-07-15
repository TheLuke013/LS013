from PySide6.QtWidgets import (QPlainTextEdit, QVBoxLayout, QWidget, 
                              QScrollBar, QApplication)
from PySide6.QtCore import (QProcess, Qt, QTimer, QByteArray, 
                           QIODevice, Signal, QProcessEnvironment)
from PySide6.QtGui import QTextCursor, QColor, QFont, QKeyEvent, QTextCharFormat
import os
import platform

class Terminal(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_terminal()
        
        self.setFocus()
        self.setFocusPolicy(Qt.StrongFocus)
        self.setUndoRedoEnabled(False)
        
        self.history = []
        self.history_index = 0
        self.current_command = ""
        self.pending_command = ""
        
    def handle_shell_output(self, data, is_error=False):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        self.process_ansi_sequences(data, cursor)
        
        self.moveCursor(QTextCursor.End)
        self.ensureCursorVisible()

    def process_ansi_sequences(self, text, cursor):
        ansi_colors = {
            '30': QColor('#000000'),  #Preto
            '31': QColor('#FF0000'),  #Vermelho
            '32': QColor('#00FF00'),  #Verde
            '33': QColor('#FFFF00'),  #Amarelo
            '34': QColor('#0000FF'),  #Azul
            '35': QColor('#FF00FF'),  #Magenta
            '36': QColor('#00FFFF'),  #Ciano
            '37': QColor('#FFFFFF'),  #Branco
            '0': None,
        }
        
        parts = text.split('\x1b[')
        if parts[0]:
            cursor.insertText(parts[0])
        
        for part in parts[1:]:
            if not part:
                continue
                
            code, *rest = part.split('m', 1)
            text_after_code = rest[0] if rest else ''
            
            fmt = QTextCharFormat()
            
            if code in ansi_colors:
                color = ansi_colors[code]
                if color:
                    fmt.setForeground(color)
                else:
                    fmt = QTextCharFormat()
                    
            cursor.setCharFormat(fmt)
            
            if text_after_code:
                cursor.insertText(text_after_code)
                
    def setup_ui(self):
        self.setFont(QFont("Consolas", 11))
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1E1E1E;
                color: #D4D4D4;
                selection-background-color: #264F78;
            }
        """)
        
        scroll_bar = self.verticalScrollBar()
        scroll_bar.setStyleSheet("""
            QScrollBar:vertical {
                background: #252526;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #3E3E42;
                min-height: 20px;
            }
        """)
    
    def setup_terminal(self):
        self.process = QProcess()
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        
        env = QProcessEnvironment.systemEnvironment()
        self.process.setProcessEnvironment(env)
        
        self.process.readyReadStandardOutput.connect(self.read_output)
        self.process.readyReadStandardError.connect(self.read_error)
        self.process.started.connect(self.on_process_start)

        if platform.system() == "Windows":
            os.system("")
            self.process.start("cmd.exe", ["/K", "prompt $G$S"], QIODevice.ReadWrite)
        else:
            env = QProcessEnvironment.systemEnvironment()
            env.insert("TERM", "xterm-256color")
            self.process.setProcessEnvironment(env)
    
    def on_process_start(self):
        self.moveCursor(QTextCursor.End)
        self.pending_command = ""

    def read_output(self):
        data = self.process.readAllStandardOutput().data().decode('utf-8', errors='replace')
        self.handle_shell_output(data)
    
    def read_error(self):
        data = self.process.readAllStandardError().data().decode('utf-8', errors='replace')
        self.handle_shell_output(data, is_error=True)

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        modifiers = event.modifiers()
        cursor = self.textCursor()
        
        if key == Qt.Key_Return or key == Qt.Key_Enter:
            self.execute_command()
        elif key == Qt.Key_Backspace:
            if cursor.positionInBlock() > 0:
                super().keyPressEvent(event)
        elif key == Qt.Key_Up:
            self.navigate_history(-1)
        elif key == Qt.Key_Down:
            self.navigate_history(1)
        elif key == Qt.Key_C and modifiers == Qt.ControlModifier:
            self.process.kill()
        elif key == Qt.Key_L and modifiers == Qt.ControlModifier:
            self.clear()
        else:
            super().keyPressEvent(event)
            self.pending_command += event.text()

    def execute_command(self):
        if not self.pending_command:
            return
            
        self.history.append(self.pending_command)
        self.history_index = len(self.history)
        
        self.process.write((self.pending_command + "\n").encode())
        self.pending_command = ""
        self.moveCursor(QTextCursor.End)

    def navigate_history(self, direction):
        if not self.history:
            return
            
        self.history_index = max(0, min(self.history_index + direction, len(self.history) - 1))
        
        cursor = self.textCursor()
        cursor.select(QTextCursor.LineUnderCursor)
        cursor.removeSelectedText()
        
        self.pending_command = self.history[self.history_index]
        cursor.insertText(self.pending_command)
        self.moveCursor(QTextCursor.End)

    def closeEvent(self, event):
        if self.process.state() == QProcess.Running:
            self.process.terminate()
            if not self.process.waitForFinished(1000):
                self.process.kill()
        super().closeEvent(event)