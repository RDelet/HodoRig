try:
    from PySide2 import QtWidgets
except:
    from PySide6 import QtWidgets

from ...Core.nameBuilder import NameBuilder


class NameBuilderUI(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self._layout = QtWidgets.QFormLayout(self)
        self._layout.setSpacing(3)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self._prefix = QtWidgets.QLineEdit("", self)
        self._type = QtWidgets.QLineEdit("", self)
        self._side = QtWidgets.QLineEdit("", self)
        self._index = QtWidgets.QLineEdit("", self)
        self._core = QtWidgets.QLineEdit("", self)
        self._suffix = QtWidgets.QLineEdit("", self)

        self._layout.addRow("Prefix", self._prefix)
        self._layout.addRow("Type", self._type)
        self._layout.addRow("Side", self._side)
        self._layout.addRow("Index", self._index)
        self._layout.addRow("Core", self._core)
        self._layout.addRow("Suffix", self._suffix)

    @property
    def name(self) -> str:
        return NameBuilder(type=self._prefix.text(),
                           side=self._type.text(),
                           index=self._side.text(),
                           prefix=self._index.text(),
                           core=self._core.text(),
                           suffix=self._suffix.text())()
