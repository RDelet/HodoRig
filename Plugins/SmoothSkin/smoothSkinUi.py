from __future__ import annotations
from typing import Optional

from PySide2 import QtWidgets, QtCore

from ...Ui.Widgets.slider import Slider
from ...Ui import utils
from .constants import SmoothMethod
from .smoothSkinCtx import SmoothSkinCtx


class SmoothSkinUi(QtWidgets.QDialog):

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(utils.main_window() if not parent else parent)
        self.setWindowTitle('Smooth Skin UI')
        self.installEventFilter(self)

        self._master_layout = QtWidgets.QFormLayout(self)
        self._master_layout.setSpacing(2)
        self._master_layout.setContentsMargins(3, 3, 3, 3)
        self._master_layout.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop)

        smooth_method = QtWidgets.QComboBox(self)
        smooth_method.addItems([method.name.title().replace("_", " ") for method in SmoothMethod])
        smooth_method.currentIndexChanged.connect(self._update_smooth_method)

        slider_height = smooth_method.rect().height() * 0.5
        radius = Slider(0, 1000, parent=self, factor=100)
        radius.setFixedHeight(slider_height)
        radius.valueChanged.connect(self._update_radius)
        radius.setValue(10)

        relax = Slider(0, 100, parent=self, factor=100)
        relax.setFixedHeight(slider_height)
        relax.valueChanged.connect(self._update_relax)
        relax.setValue(50)

        self._master_layout.addRow("Smooth Method", smooth_method)
        self._master_layout.addRow("Brush Radius", radius)
        self._master_layout.addRow("Relax Factor", relax)

    def _update_radius(self, value: float):
        print(value, value * 1e-2)
        SmoothSkinCtx.SINGLETON.radius = value * 1e-2
    
    def _update_smooth_method(self, index: int):
        SmoothSkinCtx.SINGLETON.smooth_method = SmoothMethod(index)
    
    def _update_relax(self, value: float):
        SmoothSkinCtx.SINGLETON.relax_factor = value * 0.01
