from __future__ import annotations

from typing import Optional

try:
    from PySide2 import QtGui
except:
    from PySide6 import QtGui


class StateButton(QtWidgets.QPushButton):

    def __init__(self, icon_a, icon_b, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        self.setCheckable(True)
        self.toggled.connect(self.__on_toggle_change)

        self._icon_a = icon_a
        self._icon_b = icon_b
        self.setIcon(self._icon_a)
        self.setFlat(True)

    def __on_toggle_change(self, checked: bool):
        self.setIcon(self._icon_b if checked else self._icon_a)
