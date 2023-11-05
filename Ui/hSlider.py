from PySide2 import QtCore, QtGui, QtWidgets


class HSlider(QtWidgets.QWidget):

    valueChanged = QtCore.Signal(float)

    def __init__(self, name: str, min: float = 0.0, max: float = 1000,
                 parent: QtWidgets.QWidget = None):
        super().__init__(parent)

        self._layout = QtWidgets.QHBoxLayout(self)
        self._layout.setSpacing(2)
        self._layout.setContentsMargins(0, 0, 0, 0)

        label = QtWidgets.QLabel(name, self)
        self._layout.addWidget(label)

        self._slider = QtWidgets.QSlider(self)
        self._slider.setMinimum(min)
        self._slider.setMaximum(max)
        self._slider.setOrientation(QtCore.Qt.Horizontal)
        self._layout.addWidget(self._slider)

        self._txt_value = QtWidgets.QLineEdit(str(self._slider.value()), self)
        self._txt_value.setValidator(QtGui.QDoubleValidator())
        self._layout.addWidget(self._txt_value)

        self._slider.valueChanged.connect(self._on_value_changed)
        self._txt_value.editingFinished.connect(self._on_editing_finished)

    def _on_value_changed(self, value):
        self._txt_value.setText(str(self._slider.value()))
        self.valueChanged.emit(value)
    
    def _on_editing_finished(self):
        value = float(self._txt_value.text())
        self._slider.setValue(value)
        self.valueChanged.emit(value)
    
    def set_value(self, value):
        self._slider.setValue(value)
