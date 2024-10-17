# coding=ascii

"""
!@Brief skin weights distribution tool.

File Path: {s_path}
"""

from __future__ import annotations

from enum import Enum
from functools import partial
import logging
import numpy as np
import traceback
from typing import Optional

try:
    from PySide2 import QtCore, QtGui, QtWidgets
except:
    from PySide6 import QtCore, QtGui, QtWidgets

from maya import cmds
from maya.api import OpenMaya as om2

from ..Core import constants
from ..Helpers.skin import Skin
from ..Ui import utils
from ..Ui.Widgets.selector import Selector
from ..Ui.Widgets.stateButton import StateButton
from ..Ui.Widgets.slider import Slider


log = logging.getLogger('skin Weights Distribution')
log.setLevel(logging.INFO)

kMayaMenu = True
kCategory = "Skin"
kAnnotation = "skin Weights Distribution"
kImage = None
kScriptName = 'Weights Distribution'


class WeightSolver(Enum):
    Uniform = 0
    PriorityLow = 1
    PriorityHigh = 2


class Skin:

    def __init__(self, node: Optional[str] = None):
        self._node = node
        self._shape = None
        self._influences = []
        self._weights = np.zeros((0, 0))

        if self._node:
            self.get_data()

    @property
    def influences(self) -> list:
        return self._influences

    @property
    def max_influences(self) -> int:
        return cmds.getAttr(f"{self._node}.maxInfluences")

    @property
    def maintain_max_influences(self) -> int:
        return cmds.getAttr(f"{self._node}.maintainMaxInfluences")

    @property
    def node(self) -> str:
        return self._node

    @node.setter
    def node(self, node: str):
        if not cmds.objExists(node):
            raise RuntimeError(f"Node {node} does not exists !")

        node_type = cmds.nodeType(node)
        if node_type != "skinCluster":
            raise RuntimeError(f"Node must be a skinCLuster not {node_type} !")

        self._node = node
        self.get_data()

    @property
    def shape(self) -> str:
        return self._shape

    @property
    def weights(self) -> np.array:
        return self._weights

    @weights.setter
    def weights(self, weights: np.array):
        if not self._node:
            return
        for i in range(weights.shape[0]):
            for j in range(weights.shape[1]):
                cmds.setAttr(f"{self._node}.weightList[{i}].weights[{j}]", weights[i][j])

    def set_vertex_weights(self, vertex_id: int, weights: np.array, normalize: bool = True):
        if not self._node:
            return

        if normalize:
            weights = np.round(weights, decimals=3)
            weights /= round(sum(weights), 3)

        self._weights[vertex_id] = weights
        for i in range(weights.shape[0]):
            cmds.setAttr(f"{self._node}.weightList[{vertex_id}].weights[{i}]", float(weights[i]))

    def set_vertex_influence_weight(self, vertex_id: int, influence_id: int, weight: float, normalize: bool = True):
        if not self._node:
            return

        if normalize:
            weights = self._weights[vertex_id]
            weights[influence_id] = weight
            weights /= np.sum(weights)
            self.set_vertex_weights(vertex_id, weights, normalize=False)
            return

        self._weights[vertex_id][influence_id] = weight
        cmds.setAttr(f"{self._node}.weightList[{vertex_id}].weights[{influence_id}]", float(weight))

    def _get_output_shape(self) -> Optional[str]:
        shapes = cmds.skinCluster(self._node, query=True, geometry=True)
        if shapes:
            return shapes[0]

    def get_data(self):
        if not self._node:
            return

        self._shape = self._get_output_shape()
        if not self._shape:
            raise RuntimeError(f"No output shape found on {self._node}")

        self._influences = cmds.skinCluster(self._node, query=True, influence=True)
        shape_vertices = cmds.ls(f"{self._shape}.vtx[*]", long=True, flatten=True)
        vtx_ids = cmds.getAttr(f"{self._node}.weightList", multiIndices=True)
        self._weights = np.zeros((len(shape_vertices), len(self._influences)), dtype=np.float32)

        for i in vtx_ids:
            num_inluences = cmds.getAttr(f"{self._node}.weightList[{i}].weights", multiIndices=True)
            for j in num_inluences:
                self._weights[i][j] = round(cmds.getAttr(f"{self._node}.weightList[{i}].weights[{j}]"), 4)

    @staticmethod
    def find(node: str):
        node_type = cmds.nodeType(node)
        if node_type == "skinCluster":
            return node
        elif node_type == "transform":
            shapes = cmds.listRelatives(node, shapes=True, fullPath=True)
            if not shapes:
                raise RuntimeError(f"No shape found under {node} !")
            node = shapes[0]

        history = cmds.listHistory(node)
        skins = [x for x in history if cmds.nodeType(x) == "skinCluster"]
        if not skins:
            raise RuntimeError(f"No skinCluster found on {node} !")

        return skins[0]

    @classmethod
    def get(cls, node: str):
        skin_node = cls.find(node)
        return cls(skin_node)


class WeightSlider(QtWidgets.QWidget):

    valueChanged = QtCore.Signal()
    removeClicked = QtCore.Signal()
    lockToggled = QtCore.Signal()

    def __init__(self, influence_name: str, influence_id: int, weight: float, slider_id: int,
                 parent: Optional[QtWidgets.QWidget] = None, undo_stack: Optional[QtWidgets.QUndoStack] = None):
        super().__init__(parent)
        self.undo_stack = undo_stack

        self._influence_name = influence_name
        self._influence_id = influence_id
        self._index = slider_id
        self._weight = weight
        self._old_value = self._weight

        self._build_ui()

    def _build_ui(self):
        slider_layout = QtWidgets.QHBoxLayout(self)
        slider_layout.setContentsMargins(0, 0, 0, 0)
        slider_layout.setSpacing(5)
        slider_layout.setAlignment(QtCore.Qt.AlignLeft)

        self._slider = Slider(0, 100, parent=self, undo_stack=self.undo_stack, factor=100.0)
        self._slider.setMinimumWidth(200)
        self._slider.setValue(int(self._weight * 100))
        self._slider.valueChanged.connect(self.__on_value_changed)
        self._slider.isPressed.connect(self.__on_pressed)
        self._slider.isReleased.connect(self.__on_released)
        slider_layout.addWidget(self._slider)

        self._lock_button = StateButton(constants.klockOpenIcon, constants.kLockCloseIcon, self)
        self._lock_button.toggled.connect(self.__on_lock_toggled)
        slider_layout.addWidget(self._lock_button)

        slider_height = self._slider.height()
        remove_button = QtWidgets.QPushButton(self)
        remove_button.setIcon(constants.kTrashIcon)
        remove_button.setIconSize(QtCore.QSize(slider_height, slider_height))
        remove_button.setFlat(True)
        remove_button.clicked.connect(self.__on_button_clicked)
        remove_button.setFixedSize(slider_height, slider_height)
        slider_layout.addWidget(remove_button)

    @property
    def button(self):
        return self._button

    @property
    def influence_id(self) -> int:
        return self._influence_id

    @property
    def influence_name(self) -> str:
        return self._influence_name

    @property
    def index(self) -> int:
        return self._index

    @property
    def is_lock(self) -> bool:
        return self._lock_button.isChecked()

    @property
    def old_value(self):
        return self._old_value / 100.0

    @property
    def value(self) -> float:
        return self._slider.value() / 100.0

    @value.setter
    def value(self, value: float):
        self._slider.blockSignals(True)
        self._slider.setValue(int(value * 100))
        self._slider.blockSignals(False)
        self._weight = value

    @property
    def weight(self) -> float:
        return self._weight

    def set_maximum(self, value: int):
        self._slider.lock_value = value

    def __on_button_clicked(self):
        self.removeClicked.emit()

    def __on_lock_toggled(self):
        self._slider.setEnabled(not self.is_lock)
        self.lockToggled.emit()

    @staticmethod
    def __on_pressed():
        cmds.undoInfo(openChunk=True, chunkName="EditSkinWeight")

    @staticmethod
    def __on_released():
        cmds.undoInfo(closeChunk=True)

    def __on_value_changed(self, value):
        self.valueChanged.emit()
        self._old_value = value


class SkinWeightsDistribution(QtWidgets.QDialog):

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(utils.main_window() if not parent else parent)

        self.setWindowTitle('Influence Weights Distribution')
        self.installEventFilter(self)
        self.undo_stack = QtWidgets.QUndoStack(self)

        self._skin = None
        self._weight_solver = WeightSolver.Uniform
        self._sliders = []
        self._vertex_ids = []
        self._callback_id = None

        self._master_layout = QtWidgets.QVBoxLayout(self)
        self._master_layout.setContentsMargins(5, 5, 5, 5)
        self._master_layout.setSpacing(5)
        self._master_layout.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop)

        self._build_selector_ui()
        self._build_solver_ui()
        self._build_content_ui()
        self.show()

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress:
            key = event.key()
            modifiers = QtWidgets.QApplication.keyboardModifiers()
            if key == QtCore.Qt.Key_Z and modifiers == QtCore.Qt.ControlModifier:
                self.undo_stack.undo()
                return True
            elif key == QtCore.Qt.Key_Y and modifiers == QtCore.Qt.ControlModifier:
                self.undo_stack.redo()
                return True

        return super().eventFilter(obj, event)

    def _add_separator(self):
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        self._master_layout.addWidget(separator)

    def _build_selector_ui(self):
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        self._master_layout.addLayout(layout)

        self._selector = Selector(self)
        self._selector.clicked.connect(self.__get_skin_from_selection)
        layout.addWidget(self._selector)

        self._callback_button = StateButton(constants.kSelectionOffIcon, constants.kSelectionOnIcon, self)
        self._callback_button.toggled.connect(self._on_callback_toggled)
        layout.addWidget(self._callback_button)

        self._add_separator()

    def _build_solver_ui(self):
        solver_layout = QtWidgets.QHBoxLayout()
        solver_layout.setContentsMargins(0, 0, 0, 0)
        solver_layout.setSpacing(2)
        self._master_layout.addLayout(solver_layout)

        self.radio_group = QtWidgets.QButtonGroup(self)

        rb_low = QtWidgets.QRadioButton("Low priority", self)
        rb_low.toggled.connect(partial(self._set_weight_solver, WeightSolver.PriorityLow))
        self.radio_group.addButton(rb_low)
        solver_layout.addWidget(rb_low)

        rb_high = QtWidgets.QRadioButton("High priority", self)
        rb_high.toggled.connect(partial(self._set_weight_solver, WeightSolver.PriorityHigh))
        self.radio_group.addButton(rb_high)
        solver_layout.addWidget(rb_high)

        rb_avg = QtWidgets.QRadioButton("Uniform", self)
        rb_avg.setChecked(True)
        rb_avg.toggled.connect(partial(self._set_weight_solver, WeightSolver.Uniform))
        self.radio_group.addButton(rb_avg)
        solver_layout.addWidget(rb_avg)

        self._add_separator()

    def _build_content_ui(self):
        self._content_layout = QtWidgets.QHBoxLayout(self)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(5)
        self._content_layout.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop)
        self._master_layout.addLayout(self._content_layout)

        self._influences_model = QtGui.QStandardItemModel()
        self._influences_view = QtWidgets.QTreeView(self)
        self._influences_view.setMinimumWidth(150)
        self._influences_view.setModel(self._influences_model)
        self._influences_view.header().setVisible(False)
        self._influences_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self._influences_view.customContextMenuRequested.connect(self._item_menu_requested)
        self._content_layout.addWidget(self._influences_view)

        self._slider_layout = QtWidgets.QFormLayout(self)
        self._slider_layout.setLabelAlignment(QtCore.Qt.AlignLeft)
        self._slider_layout.setContentsMargins(0, 0, 0, 0)
        self._slider_layout.setSpacing(5)
        self._content_layout.addLayout(self._slider_layout)

    def _on_callback_toggled(self):
        self._init_callback() if self._callback_button.isChecked() else self._remove_callback()

    def _on_selection_changed(self, *args, **kwargs):
        if not self._skin:
            return

        self._vertex_ids = []
        selection_list = om2.MGlobal.getActiveSelectionList()
        for i in range(selection_list.length()):
            path, components = selection_list.getComponent(i)
            if not path.fullPathName().endswith(self._skin.shape):
                continue
            if components and components.apiType() == om2.MFn.kMeshVertComponent:
                cfn = om2.MFnSingleIndexedComponent(components)
                self._vertex_ids = cfn.getElements()
                self._update_from_vertex()
                return

    def _init_callback(self):
        self._callback_id = om2.MModelMessage.addCallback(om2.MModelMessage.kActiveListModified,
                                                          self._on_selection_changed)

    def _remove_callback(self):
        if self._callback_id:
            om2.MMessage.removeCallback(self._callback_id)

    def _item_menu_requested(self, position: QtCore.QPoint):
        index = self._influences_view.indexAt(position)
        if not index.isValid():
            return

        add_influence = QtWidgets.QAction("Add influence", self)
        add_influence.triggered.connect(partial(self._add_influence, index))

        menu = QtWidgets.QMenu(self)
        menu.addAction(add_influence)
        menu.exec_(self._influences_view.viewport().mapToGlobal(position))

    def _add_influence(self, index: QtCore.QModelIndex):
        if not index.isValid():
            return

        if self._skin.maintain_max_influences and len(self._sliders) == self._skin.max_influences:
            utils.error_dialog(self, f"Max influence already reached !")
            return

        influence_name = index.data()
        influence_id = index.row()
        influences_ids = [x.influence_id for x in self._sliders]
        if influence_id in influences_ids:
            utils.error_dialog(self, f"Influence {influence_name} already in {self._skin.node}")
            return

        self._add_slider(index.data(), influence_id, 0.0)

    def _clear_sliders(self):
        while self._slider_layout.count():
            item = self._slider_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            self._slider_layout.removeItem(item)

        self._sliders.clear()

    def __get_influence_ids(self) -> list:
        influence_ids = []
        for vertex_id in self._vertex_ids:
            vertex_weights = self._skin.weights[vertex_id]
            influence_ids.extend(np.where(vertex_weights > 0.0)[0])

        return list(set(influence_ids))

    def _update_from_vertex(self):
        influence_ids = self.__get_influence_ids()

        vertex_weights = self._skin.weights[self._vertex_ids[-1]]
        influence_weights = vertex_weights[influence_ids]

        self._clear_sliders()
        self._build_sliders(influence_ids, influence_weights)

    def _add_slider(self, influence: str, influence_id: int, weight: float) -> WeightSlider:
        slider_id = len(self._sliders)
        slider = WeightSlider(influence, influence_id, weight, slider_id, parent=self, undo_stack=self.undo_stack)
        slider.valueChanged.connect(self._update_weights)
        slider.removeClicked.connect(self._remove_weights)
        slider.lockToggled.connect(self._lock_toggled)

        self._slider_layout.addRow(slider.influence_name.split("|")[-1].split(":")[-1], slider)
        self._sliders.append(slider)

        return slider

    def _build_sliders(self, influence_ids, influence_weights):
        for i in range(len(influence_ids)):
            influence = self._skin.influences[influence_ids[i]]
            self._add_slider(influence, influence_ids[i], influence_weights[i])

    def _set_weight_solver(self, solver, _):
        self._weight_solver = solver

    def __get_skin_from_selection(self):
        selection = cmds.ls(selection=True, long=True)
        if not selection:
            utils.error_dialog(self, "No node selected !")

        try:
            self._skin = Skin.get(selection[0])
            self._selector.set_text(self._skin.node)
            self._influences_model.clear()
            for influence in self._skin.influences:
                item = QtGui.QStandardItem(influence.split("|")[-1].split(":")[-1])
                self._influences_model.appendRow(item)
        except Exception as e:
            utils.error_dialog(self, str(e))

    def _lock_toggled(self):
        locked_weights = [x.weight for x in self._sliders if x.is_lock]
        max_value = 1 - sum(locked_weights)
        for slider in self._sliders:
            if slider.is_lock:
                continue
            slider.set_maximum(max_value * 100)

    def _update_weights(self):
        sender_widget = self.sender()
        if self._weight_solver == WeightSolver.PriorityLow:
            self._normalize_low_priority(sender_widget)
        elif self._weight_solver == WeightSolver.PriorityHigh:
            self._normalize_high_priority(sender_widget)
        elif self._weight_solver == WeightSolver.Uniform:
            self._normalize_uniform(sender_widget)

    def _normalize_low_priority(self, slider: WeightSlider):
        unlock_slider_ids = [x.influence_id for x in self._sliders if not x.is_lock and x != slider]
        slider_ids = [x.influence_id for x in self._sliders]
        if not unlock_slider_ids:
            return

        weights = self._get_weights(slider)
        weights_to_change = np.maximum(weights[unlock_slider_ids], 1e-8)
        if not weights_to_change.any():
            return

        delta = slider.old_value - slider.value
        inv_weights = 1.0 / weights_to_change
        weights[unlock_slider_ids] = np.maximum(weights_to_change + (inv_weights / sum(inv_weights)) * delta, 1e-8)

        self._set_weights(weights[slider_ids])

    def _normalize_high_priority(self, slider: WeightSlider):
        unlock_slider_ids = [x.influence_id for x in self._sliders if not x.is_lock and x != slider]
        slider_ids = [x.influence_id for x in self._sliders]
        if not unlock_slider_ids:
            return

        weights = self._get_weights(slider)
        weights_to_change = np.maximum(weights[unlock_slider_ids], 1e-8)
        if not weights_to_change.any():
            return

        delta = slider.old_value - slider.value
        weights[unlock_slider_ids] = weights_to_change + (weights_to_change / sum(weights_to_change)) * delta

        self._set_weights(weights[slider_ids])

    def _normalize_uniform(self, slider: WeightSlider):
        locked_slider_ids = [x.influence_id for x in self._sliders if x.is_lock or x == slider]
        unlock_slider_ids = [x.influence_id for x in self._sliders if not x.is_lock and x != slider]
        slider_ids = [x.influence_id for x in self._sliders]
        if not unlock_slider_ids:
            return

        weights = self._get_weights(slider)
        weights_to_change = np.maximum(weights[unlock_slider_ids], 1e-8)
        if not weights_to_change.any():
            return

        remaining_sum = (slider.old_value - slider.value) / len(weights_to_change)
        new_weights = np.maximum(weights_to_change + remaining_sum, 1e-8)
        weights[unlock_slider_ids] = new_weights * ((1 - np.sum(weights[locked_slider_ids])) / sum(new_weights))

        self._set_weights(weights[slider_ids])

    def _get_weights(self, slider: WeightSlider) -> np.array:
        weights = self._skin.weights[self._vertex_ids[-1]]
        weights[slider.influence_id] = slider.value

        return weights

    def _remove_weights(self):
        sender = self.sender()
        # Remove weight from selected influence
        for vtx_id in self._vertex_ids:
            self._skin.set_vertex_influence_weight(vtx_id, sender.influence_id, 0.0)
        # Rebuild sliders
        self._clear_sliders()
        self._update_from_vertex()

    def _set_weights(self, new_weights: np.array):
        # Set sliders
        for slider, w in zip(self._sliders, new_weights):
            slider.value = w
        # Set weights
        influence_ids = [x.influence_id for x in self._sliders]
        for vertex_id in self._vertex_ids:
            weights = self._skin.weights[vertex_id]
            weights[influence_ids] = new_weights
            self._skin.set_vertex_weights(vertex_id, weights)


def main():
    try:
        SkinWeightsDistribution()
    except Exception:
        log.error(traceback.format_exc())
