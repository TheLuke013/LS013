import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QVBoxLayout,
                               QWidget, QFileDialog, QMenuBar, QMenu, QStatusBar)
from PySide6.QtGui import QFont, QTextCharFormat, QColor, QSyntaxHighlighter, QTextCursor, QAction, QFont
from PySide6.QtCore import Qt, QRegularExpression

class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.highlightingRules = []
        
        keyword_color = QColor("#569CD6")
        class_function_color = QColor("#4EC9B0")
        string_color = QColor("#CE9178")
        comment_color = QColor("#6A9955")
        number_color = QColor("#B5CEA8")
        self_color = QColor("#9CDCFE")
        
        keywords = [
            "and", "as", "assert", "break", "class", "continue", "def",
            "del", "elif", "else", "except", "False", "finally", "for",
            "from", "global", "if", "import", "in", "is", "lambda",
            "None", "nonlocal", "not", "or", "pass", "raise", "return",
            "True", "try", "while", "with", "yield"
        ]
        
        for word in keywords:
            pattern = QRegularExpression(f"\\b{word}\\b")
            format = QTextCharFormat()
            format.setForeground(keyword_color)
            format.setFontWeight(QFont.Weight.Bold)
            self.highlightingRules.append((pattern, format))
        
        class_function_format = QTextCharFormat()
        class_function_format.setForeground(class_function_color)
        class_function_format.setFontWeight(QFont.Weight.Bold)
        self.highlightingRules.append((QRegularExpression("\\bclass\\s+(\\w+)"), class_function_format))
        self.highlightingRules.append((QRegularExpression("\\bdef\\s+(\\w+)"), class_function_format))
        
        string_format = QTextCharFormat()
        string_format.setForeground(string_color)
        self.highlightingRules.append((QRegularExpression("\"[^\"]*\""), string_format))
        self.highlightingRules.append((QRegularExpression("'[^']*'"), string_format))
        
        comment_format = QTextCharFormat()
        comment_format.setForeground(comment_color)
        comment_format.setFontItalic(True)
        self.highlightingRules.append((QRegularExpression("#[^\n]*"), comment_format))
        
        number_format = QTextCharFormat()
        number_format.setForeground(number_color)
        self.highlightingRules.append((QRegularExpression("\\b[0-9]+\\b"), number_format))
        
        docstring_format = QTextCharFormat()
        docstring_format.setForeground(QColor("#608B4E"))
        self.highlightingRules.append((QRegularExpression(r'"""[^"]*"""'), docstring_format))
        self.highlightingRules.append((QRegularExpression(r"'''[^']*'''"), docstring_format))
        
        decorator_format = QTextCharFormat()
        decorator_format.setForeground(QColor("#C586C0"))
        self.highlightingRules.append((QRegularExpression(r'@\w+'), decorator_format))
        
        self_format = QTextCharFormat()
        self_format.setForeground(self_color)
        self.highlightingRules.append((QRegularExpression("\\bself\\b"), self_format))
    
    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)