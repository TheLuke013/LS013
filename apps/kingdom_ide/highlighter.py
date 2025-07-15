import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QVBoxLayout,
                               QWidget, QFileDialog, QMenuBar, QMenu, QStatusBar)
from PySide6.QtGui import QFont, QTextCharFormat, QColor, QSyntaxHighlighter, QTextCursor, QAction, QFont
from PySide6.QtCore import Qt, QRegularExpression

class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.highlightingRules = []

        blue_dark = QColor("#569CD6")
        lilac = QColor("#C586C0")
        cyan_green = QColor("#4EC9B0")
        light_yellow = QColor("#DCDCAA") 
        string_color = QColor("#CE9178")
        comment_color = QColor("#6A9955")
        number_color = QColor("#B5CEA8")
        function_color = QColor("#DCDCAA")
        
        builtins = [
                "abs", "all", "any", "ascii", "bin", "bool", "breakpoint", "bytearray", "bytes",
                "callable", "chr", "classmethod", "compile", "complex", "delattr", "dict", "dir",
                "divmod", "enumerate", "eval", "exec", "filter", "float", "format", "frozenset",
                "getattr", "globals", "hasattr", "hash", "help", "hex", "id", "input", "int",
                "isinstance", "issubclass", "iter", "len", "list", "locals", "map", "max", "memoryview",
                "min", "next", "object", "oct", "open", "ord", "pow", "print", "property", "range",
                "repr", "reversed", "round", "set", "setattr", "slice", "sorted", "staticmethod",
                "str", "sum", "super", "tuple", "type", "vars", "zip", "__import__"
            ]

        blue_keywords = [
                "class",
                "def",
                "self",
                "True", 
                "False",
                "None",
                "is",
                "not",
                "or",
                "and"
        ]
        
        lilac_keywords = [
                "import",
                "from",
                "if", 
                "else",
                "elif", 
                "while",
                "for", 
                "return", 
                "try", 
                "except",
                "with",
                "break",
                "pass",
                "finally",
                "raise",
                "assert",
                "global",
                "nonlocal",
                "async",
                "await",
                "in"
             ]

        for word in blue_keywords:
            pattern = QRegularExpression(f"\\b{word}\\b")
            fmt = QTextCharFormat()
            fmt.setForeground(blue_dark)
            fmt.setFontWeight(QFont.Weight.Bold)
            self.highlightingRules.append((pattern, fmt))

        for word in lilac_keywords:
            pattern = QRegularExpression(f"\\b{word}\\b")
            fmt = QTextCharFormat()
            fmt.setForeground(lilac)
            fmt.setFontWeight(QFont.Weight.Bold)
            self.highlightingRules.append((pattern, fmt))
            
        builtin_function_format = QTextCharFormat()
        builtin_function_format.setForeground(function_color)
        builtin_function_format.setFontItalic(True)

        for word in builtins:
            pattern = QRegularExpression(f"\\b{word}\\b(?=\\s*\\()")
            self.highlightingRules.append((pattern, builtin_function_format))


        class_name_pattern = QRegularExpression(r"\bclass\s+(\w+)")
        class_name_format = QTextCharFormat()
        class_name_format.setForeground(cyan_green)
        class_name_format.setFontWeight(QFont.Weight.Bold)
        self.highlightingRules.append((class_name_pattern, class_name_format))

        def_keyword_format = QTextCharFormat()
        def_keyword_format.setForeground(QColor("#569CD6"))
        def_keyword_format.setFontWeight(QFont.Weight.Bold)
        self.highlightingRules.append((QRegularExpression(r"\bdef\b"), def_keyword_format))

        func_name_format = QTextCharFormat()
        func_name_format.setForeground(function_color)
        func_name_format.setFontWeight(QFont.Weight.Bold)
        self.highlightingRules.append((QRegularExpression(r"\bdef\s+(\w+)"), func_name_format))

        string_format = QTextCharFormat()
        string_format.setForeground(string_color)
        self.highlightingRules.append((QRegularExpression(r'"[^"]*"'), string_format))
        self.highlightingRules.append((QRegularExpression(r"'[^']*'"), string_format))
        
        self.triple_single_quote = QRegularExpression("'''")
        self.triple_double_quote = QRegularExpression('"""')

        self.multi_line_string_format = QTextCharFormat()
        self.multi_line_string_format.setForeground(QColor("#CE9178"))

        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor("#6A9955"))
        self.comment_format.setFontItalic(True)

        number_format = QTextCharFormat()
        number_format.setForeground(number_color)
        self.highlightingRules.append((QRegularExpression(r"\b\d+\b"), number_format))

        docstring_format = QTextCharFormat()
        docstring_format.setForeground(comment_color)
        self.highlightingRules.append((QRegularExpression(r'"""[^"]*"""'), docstring_format))
        self.highlightingRules.append((QRegularExpression(r"'''[^']*'''"), docstring_format))

        decorator_format = QTextCharFormat()
        decorator_format.setForeground(lilac)
        self.highlightingRules.append((QRegularExpression(r"@\w+"), decorator_format))

        symbol_format = QTextCharFormat()
        symbol_format.setForeground(QColor("#ffbc05"))
        self.highlightingRules.append((QRegularExpression(r"[()\[\]]"), symbol_format))

    def highlightBlock(self, text):
        for pattern, fmt in self.highlightingRules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                if match.lastCapturedIndex() > 0:
                    for i in range(1, match.lastCapturedIndex() + 1):
                        self.setFormat(match.capturedStart(i), match.capturedLength(i), fmt)
                else:
                    self.setFormat(match.capturedStart(), match.capturedLength(), fmt)

        self.setCurrentBlockState(0)
        multiline_ranges = []

        in_multiline, ranges1 = self.match_multiline(text, self.triple_double_quote, self.multi_line_string_format)
        multiline_ranges.extend(ranges1)
        if not in_multiline:
            in_multiline, ranges2 = self.match_multiline(text, self.triple_single_quote, self.multi_line_string_format)
            multiline_ranges.extend(ranges2)

        string_regex = QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"|\'[^\'\\]*(\\.[^\'\\]*)*\'')
        it = string_regex.globalMatch(text)
        while it.hasNext():
            match = it.next()
            multiline_ranges.append((match.capturedStart(), match.capturedEnd()))

        def is_inside_string(pos):
            for start, end in multiline_ranges:
                if start <= pos < end:
                    return True
            return False

        comment_index = text.find("#")
        while comment_index != -1:
            if not is_inside_string(comment_index):
                self.setFormat(comment_index, len(text) - comment_index, self.comment_format)
                break
            comment_index = text.find("#", comment_index + 1)

    def match_multiline(self, text, delimiter, fmt):
        ranges = []
        start_delim = delimiter.pattern()
        start = 0
        add = 0

        if self.previousBlockState() != 1:
            start_match = delimiter.match(text)
            if start_match.hasMatch():
                start = start_match.capturedStart()
                add = start_match.capturedLength()
            else:
                return False, ranges
        else:
            start = 0

        end_match = delimiter.match(text, start + add)
        if end_match.hasMatch():
            end = end_match.capturedEnd()
            length = end - start
            self.setFormat(start, length, fmt)
            ranges.append((start, end))
            return True, ranges
        else:
            self.setFormat(start, len(text) - start, fmt)
            self.setCurrentBlockState(1)
            ranges.append((start, len(text)))
            return True, ranges