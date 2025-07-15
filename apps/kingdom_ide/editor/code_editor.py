from PySide6.QtGui import QFont, QTextCursor, QColor, QPainter, QTextFormat, QTextCursor
from PySide6.QtWidgets import (QWidget, QPlainTextEdit , QVBoxLayout,
                              QFileDialog, QStatusBar)
from PySide6.QtCore import Qt, QTimer, QSize, QRect
import os

from apps.kingdom_ide.highlighter import PythonHighlighter

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
    
    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)
    
    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)

class CodeEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.setFont(QFont("Consolas", 12))
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.highlighter = PythonHighlighter(self.document())
        
        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        
        self.setTabStopDistance(40)
        
        self.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12pt;
                background-color: #1E1E1E;
                color: #D4D4D4;
                selection-background-color: #264F78;
            }
        """)
        
        self.setInputMethodHints(Qt.InputMethodHint.ImhMultiLine | 
                               Qt.InputMethodHint.ImhNoPredictiveText)
        
        self._is_modified = False
        self.document().contentsChanged.connect(self._on_modification_change)
        
        self.setup_scrollbar_style()
    
    def line_number_area_width(self):
        digits = len(str(max(1, self.blockCount())))
        space = 10 + self.fontMetrics().horizontalAdvance('9') * digits
        return space
    
    def update_line_number_area_width(self):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
    
    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), 
                                       self.line_number_area.width(), 
                                       rect.height())
        
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width()
    
    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#1E1E1E"))
        
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        
        font = painter.font()
        font.setFamily("Consolas")
        font.setPointSize(12)
        painter.setFont(font)
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor("#858585"))
                painter.drawText(0, top, 
                               self.line_number_area.width() - 5, 
                               self.fontMetrics().height(),
                               Qt.AlignmentFlag.AlignRight, number)
            
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(),
                                             self.line_number_area_width(), 
                                             cr.height()))        
    def _on_modification_change(self):
        self._is_modified = True
        if hasattr(self.parent(), 'update_title'):
            self.parent().update_title(True)
    
    def setup_scrollbar_style(self):
        scrollbar_style = """
        QPlainTextEdit {
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 12pt;
            background-color: #1E1E1E;
            color: #D4D4D4;
            selection-background-color: #264F78;
        }
        /* ... restante do estilo ... */
        """
        self.setStyleSheet(self.styleSheet() + scrollbar_style)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return:
            cursor = self.textCursor()
            current_line = cursor.block().text()
            
            indentation = len(current_line) - len(current_line.lstrip())
            
            if current_line.rstrip().endswith(':'):
                indentation += 4
            
            super().keyPressEvent(event)
            cursor.insertText(" " * indentation)
        else:
            super().keyPressEvent(event)