from __future__ import annotations


try:
    from PySide2.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor
    from PySide2.QtCore import QRegExp
    def find_regex(regex, text):
        return regex.indexIn(text) > -1
except ImportError:
    from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor
    from PySide6.QtCore import QRegularExpression as QRegExp
    def find_regex(regex, text):
        return regex.match(text).hasMatch()


class SyntaxHighLigther(QSyntaxHighlighter):

    kWhite = QColor(200, 200, 200)
    kRed = QColor(255, 125, 160)
    kOrange = QColor(255, 130, 20)
    kGreen = QColor(35, 170, 30)
    kBlue = QColor(35, 170, 30)

    rx_error = QRegExp(r'[Ee][Rr][Rr][Oo][Rr]')
    rx_warning = QRegExp(r'[Ww][Aa][Rr][Nn][Ii][Nn][Gg]')
    rx_debug = QRegExp(r'[Dd][Ee][Bb][Uu][Gg]')
    rx_info = QRegExp(r'[Ii][Nn][Ff][Oo]')

    def __init__(self, parent):
        super().__init__(parent.document() if hasattr(parent, 'document') else parent)
        self.parent = parent

    def highlightBlock(self, text):
        keyword = QTextCharFormat()
        
        if find_regex(self.rx_error, text):
            keyword.setForeground(self.kRed)
        elif find_regex(self.rx_warning, text):
            keyword.setForeground(self.kOrange)
        elif find_regex(self.rx_debug, text):
            keyword.setForeground(self.kGreen)
        elif find_regex(self.rx_info, text):
            keyword.setForeground(self.kBlue)
        else:
            keyword.setForeground(self.kWhite)
        
        self.setFormat(0, len(text), keyword)
        self.setCurrentBlockState(0)

    @classmethod
    def add_on_widget(cls, widget) -> SyntaxHighLigther:
        return cls(widget)
