from __future__ import annotations

from typing import Optional

from PySide2 import QtCore, QtWidgets


class Selector(QtWidgets.QWidget):

    clicked = QtCore.Signal()

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        self.setLayout(layout)

        self._line_edit = QtWidgets.QLineEdit(self)
        self._line_edit.setEnabled(False)
        layout.addWidget(self._line_edit)

        button = QtWidgets.QPushButton("<<", self)
        button.setFixedWidth(button.height())
        button.clicked.connect(self.__on_clicked)
        layout.addWidget(button)

    def __on_clicked(self):
        self.clicked.emit()

    def set_text(self, txt):
        self._line_edit.setText(txt)
