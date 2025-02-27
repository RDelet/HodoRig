from __future__ import annotations
from typing import Optional

from PySide2 import QtWidgets, QtCore

from ...Ui.Widgets.slider import Slider
from ...Ui import utils
from . import constants
from .smoothSkinCtx import SmoothSkinCtx


class SmoothSkinUi(QtWidgets.QDialog):

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(utils.main_window() if not parent else parent)
        self.setWindowTitle('Smooth Skin UI')
        self.installEventFilter(self)

        self._master_layout = QtWidgets.QVBoxLayout(self)
        self._master_layout.setContentsMargins(5, 5, 5, 5)
        self._master_layout.setSpacing(5)
        self._master_layout.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop)

        slider = Slider(0, 100, parent=self)
        slider.setValue(10)
        slider.valueChanged.connect(self._update_radius)
        self._master_layout.addWidget(slider)

    def _update_radius(self, value: float):
        SmoothSkinCtx.SINGLETON.radius = value
