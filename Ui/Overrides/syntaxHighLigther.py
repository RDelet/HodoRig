from typing import Optional

try:
    from PySide2 import QtCore, QtGui, QtWidgets
except:
    from PySide6 import QtCore, QtGui, QtWidgets

from ...Ui import utils as uiUtils


class SyntaxHighLigther(QtGui.QSyntaxHighlighter):

    kWhite = QtGui.QColor(200, 200, 200)
    kRed = QtGui.QColor(255, 125, 160)
    kOrange = QtGui.QColor(255, 130, 20)
    kGreen = QtGui.QColor(35, 170, 30)
    kBlue = QtGui.QColor(35, 170, 30)

    rx_error = QtCore.QRegExp(r'[Ee][Rr][Rr][Oo][Rr]')
    rx_warning = QtCore.QRegExp(r'[Ww][Aa][Rr][Nn][Ii][Nn][Gg]')
    rx_debug = QtCore.QRegExp(r'[De][Ee][Bb][Uu][Gg]')
    rx_info = QtCore.QRegExp(r'[Ii][Nn]][Fo][Oo]')

    kBaseName = None

    def __init__(self, parent):
        super().__init__(parent.document())
        self.parent = parent

    def highlightBlock(self, t):
        keyword = QtGui.QTextCharFormat()

        if self.rx_error.indexIn(t) > 0:
            keyword.setForeground(self.kRed)
        elif self.rx_warning.indexIn(t) > 0:
            keyword.setForeground(self.kOrange)
        elif self.rx_debug.indexIn(t) > 0:
            keyword.setForeground(self.kGreen)
        elif self.rx_info.indexIn(t) > 0:
            keyword.setForeground(self.kBlue)
        else:
            keyword.setForeground(self.kWhite)

        self.setFormat(0, len(t), keyword)
        self.setCurrentBlockState(0)

    @classmethod
    def focus_changed_cb(cls, old_widget: QtWidgets.QWidget, new_widget: QtWidgets.QWidget):
        if new_widget:
            widget_name = new_widget.objectName()
            if cls.kBaseName and not widget_name.startswith(cls.kBaseName):
                return
            cls.add_on_widget(widget_name)

    @classmethod
    def add_on_widget(cls, control_name: str) -> Optional["SyntaxHighLigther"]:
        widget = uiUtils.find_control(control_name, widget_cls=QtWidgets.QTextEdit)
        if widget:
            return cls(widget)
        
        return None
