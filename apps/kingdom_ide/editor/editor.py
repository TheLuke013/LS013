from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QWidget, QTextEdit, QVBoxLayout,
                              QFileDialog, QStatusBar)
from PySide6.QtCore import Qt
import os

from apps.kingdom_ide.highlighter import PythonHighlighter

class CodeEditor(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setFont(QFont("Consolas", 12))
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.highlighter = PythonHighlighter(self.document())
        
        self.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12pt;
                background-color: #1E1E1E;
                color: #D4D4D4;
                selection-background-color: #264F78;
            }
        """)
        
        self.setAcceptRichText(False)
        self.setInputMethodHints(Qt.InputMethodHint.ImhMultiLine | 
                               Qt.InputMethodHint.ImhNoPredictiveText)
        
        self._is_modified = False
        self.document().contentsChanged.connect(self._on_modification_change)
        
        self.setup_scrollbar_style()
    
    def _on_modification_change(self):
        self._is_modified = True
        if hasattr(self.parent(), 'update_title'):
            self.parent().update_title(True)
    
    def setup_scrollbar_style(self):
        scrollbar_style = """
        /* Barra de rolagem vertical */
        QScrollBar:vertical {
            border: none;
            background: #252526;
            width: 12px;
            margin: 0px;
        }
        
        QScrollBar::handle:vertical {
            background: #3E3E42;
            min-height: 20px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:vertical:hover {
            background: #5E5E60;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
            background: none;
        }
        
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }
        
        /* Barra de rolagem horizontal */
        QScrollBar:horizontal {
            border: none;
            background: #252526;
            height: 12px;
            margin: 0px;
        }
        
        QScrollBar::handle:horizontal {
            background: #3E3E42;
            min-width: 20px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background: #5E5E60;
        }
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
            background: none;
        }
        
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
            background: none;
        }
        """
        self.setStyleSheet(self.styleSheet() + scrollbar_style)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return:
            cursor = self.textCursor()
            current_line = cursor.block().text()
            
            indentation = len(current_line) - len(current_line.lstrip())
            
            if current_line.rstrip().endswith(':'):
                indentation += 4
            
            indentation = (indentation // 4) * 4
            
            super().keyPressEvent(event) 
            cursor.insertText(" " * indentation)
        else:
            super().keyPressEvent(event)

class PythonEditor(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.editor = CodeEditor()
        layout.addWidget(self.editor)
        
        self.status_bar = QStatusBar()
        layout.addWidget(self.status_bar)
        self.status_bar.showMessage("Pronto")
        
        self.current_file = None
        
        self.setStyleSheet("""
            QWidget {
                background-color: #1E1E1E;
                color: #D4D4D4;
            }
            QTextEdit {
                background-color: #1E1E1E;
                color: #D4D4D4;
                selection-background-color: #264F78;
            }
            QStatusBar {
                background-color: #007ACC;
                color: #FFFFFF;
                padding: 0px;
                margin: 0px;
            }
        """)
    
    def update_title(self, modified=False):
        title = "Editor"
        if self.current_file:
            title = os.path.basename(self.current_file)
        if modified:
            title += " *"
        self.setWindowTitle(title)
    
    def undo(self):
        self.editor.undo()

    def redo(self):
        self.editor.redo()

    def cut(self):
        self.editor.cut()

    def copy(self):
        self.editor.copy()

    def paste(self):
        self.editor.paste()
        
    def clear(self):
        self.editor.clear()
        self.current_file = None
        self.status_bar.showMessage("Editor limpo")
    
    def detect_file_encoding(self, file_path):
        import chardet
        
        with open(file_path, 'rb') as f:
            rawdata = f.read()
            result = chardet.detect(rawdata)
            encoding = result['encoding']
            
            test_text = rawdata.decode(encoding, errors='replace')
            if 'Ã' in test_text or 'Â' in test_text:
                for enc in ['utf-8', 'latin-1', 'cp1252']:
                    try:
                        test_text = rawdata.decode(enc, errors='strict')
                        if 'Ã' not in test_text and 'Â' not in test_text:
                            return enc
                    except:
                        continue
            return encoding
    
    def fix_encoding_issues(self, text):
        replacements = {
            'á': 'á', 'é': 'é', 'í': 'í', 'ó': 'ó', 'ú': 'ú',
            'ã': 'ã', 'õ': 'õ', 'â': 'â', 'ê': 'ê', 'ç': 'ç',
            'à': 'à', 'À': 'À', 'É': 'É', 'Ó': 'Ó',
        }
        
        for wrong, correct in replacements.items():
            text = text.replace(wrong, correct)
            
        return text
    
    def open_file(self, file_name):
        try:
            encoding = self.detect_file_encoding(file_name)
            
            with open(file_name, 'r', encoding=encoding) as f:
                content = f.read()
                
            content = self.fix_encoding_issues(content)
                
            self.editor.setPlainText(content)
            self.current_file = file_name
            return True
        except Exception as e:
            return str(e)
    
    def save_file(self):
        if self.current_file:
            try:
                with open(self.current_file, 'w', encoding='utf-8') as f:
                    f.write(self.editor.toPlainText())
                self.status_bar.showMessage(f"Arquivo salvo: {self.current_file}")
                return True
            except Exception as e:
                self.status_bar.showMessage(f"Erro ao salvar: {str(e)}")
                return False
        else:
            return self.save_file_as()
            
    def save_file_as(self):
        file_name, _ = QFileDialog.getSaveFileName(
            self, 
            "Salvar Arquivo", 
            "", 
            "Arquivos Python (*.py);;Todos os Arquivos (*)"
        )
        
        if file_name:
            if not file_name.endswith('.py'):
                file_name += '.py'
            self.current_file = file_name
            return self.save_file()
        return False