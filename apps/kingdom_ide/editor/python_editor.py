from PySide6.QtWidgets import (QWidget, QPlainTextEdit , QVBoxLayout,
                              QFileDialog, QStatusBar)
import os

from apps.kingdom_ide.editor.code_editor import CodeEditor

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