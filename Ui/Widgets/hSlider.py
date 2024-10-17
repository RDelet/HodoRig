try:
    from PySide2 import QtCore, QtGui, QtWidgets
except:
    from PySide6 import QtCore, QtGui, QtWidgets


class HSlider(QtWidgets.QWidget):

    valueChanged = QtCore.Signal(float)

    def __init__(self, name: str, min: float = 0.0, max: float = 1000,
                 parent: QtWidgets.QWidget = None):
        super().__init__(parent)

        self._max = max

        self._layout = QtWidgets.QHBoxLayout(self)
        self._layout.setSpacing(2)
        self._layout.setContentsMargins(0, 0, 0, 0)

        if name:
            label = QtWidgets.QLabel(name, self)
            self._layout.addWidget(label)

        self._slider = QtWidgets.QSlider(self)
        self._slider.setMinimum(min)
        self._slider.setMaximum(self._max)
        self._slider.setOrientation(QtCore.Qt.Horizontal)
        self._layout.addWidget(self._slider)

        self._txt_value = QtWidgets.QLineEdit(str(self.value), self)
        self._txt_value.setValidator(QtGui.QDoubleValidator())
        self._layout.addWidget(self._txt_value)

        self._slider.valueChanged.connect(self._on_value_changed)
        self._txt_value.editingFinished.connect(self._on_editing_finished)

    def _on_value_changed(self, value):
        self._txt_value.setText(str(self.value))
        self.valueChanged.emit(value)
    
    def _on_editing_finished(self):
        value = float(self._txt_value.text())
        self.value = value
        self.valueChanged.emit(value)
    
    @property
    def value(self):
        return self._slider.value()

    @value.setter
    def value(self, value):
        if value > self._max:
            self._max = value
            self._slider.setMaximum(self._max)
        self._slider.setValue(value)
