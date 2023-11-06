import os
import typing

import PySide2.QtCore
import PySide2.QtWidgets

from maya import cmds

from PySide2 import QtCore, QtWidgets

from HodoRig.Ui import utils
from HodoRig.Ui.colorWidget import ColorWidget
from HodoRig.Ui.hSlider import HSlider
from HodoRig.Core import constants
from HodoRig.Builders.shape import Shape
from HodoRig.Nodes.manip import Manip


class ShapeItem(QtWidgets.QListWidgetItem):

    def __init__(self, path, *args, **kwargs):

        self.path = path
        self.name = os.path.split(path)[-1].split(".")[0]

        super().__init__(self.name, *args, **kwargs)
    
    @property
    def icon(self) -> str:
        dir, _ = os.path.split(self.path)
        return os.path.join(dir, f"{self.name}.{constants.kIconExtension}")


class ShapeView(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self._layout = QtWidgets.QVBoxLayout(self)
        self._layout.setSpacing(2)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.scale_factor = 1.0

        self._list_view = QtWidgets.QListWidget(self)
        self._list_view.itemDoubleClicked.connect(self._build_manip)
        self._layout.addWidget(self._list_view)

        self._manip_name()

        self._save_shape = QtWidgets.QPushButton("Save Shape", self)
        self._layout.addWidget(self._save_shape)
        self._save_shape.clicked.connect(self.dump_shape)

        self.update_content()
    
    def _manip_name(self):
        widget = QtWidgets.QWidget(self)
        self._layout.addWidget(widget)

        layout = QtWidgets.QHBoxLayout(widget)
        layout.setSpacing(3)
        layout.setContentsMargins(0, 0, 0, 0)

        label = QtWidgets.QLabel("Manip Name", self)
        layout.addWidget(label)

        self._name = QtWidgets.QLineEdit("", self)
        layout.addWidget(self._name)
    
    @staticmethod
    def get_shape() -> list:
        p = constants.kShapeDir
        return [ShapeItem(os.path.join(p, x)) for x in os.listdir(p)]
    
    def update_content(self):
        self._list_view.clear()
        [self._list_view.addItem(item) for item in self.get_shape()]
    
    def dump_shape(self):
        selected = cmds.ls(selection=True, long=True)
        if len(selected) > 1:
            raise RuntimeError("select one node !")

        file_name, valid = QtWidgets.QInputDialog.getText(self, 'File Name', 'Give file name')
        if not valid:
            return
        if not file_name:
            raise RuntimeError("No name given !")

        if file_name in self.get_shape():
            raise RuntimeError(f"File {file_name}.{constants.kShapeExtension} already exists!")

        new_shape = Shape()
        new_shape.get_from_node(selected[0])
        new_shape.dump(file_name)

        self.update_content()
    
    def _build_manip(self, item: ShapeItem = None):

        if not item:
            selected = self._list_view.selectedItems()
            if selected:
                item = selected[0]
            else:
                raise RuntimeError("No item selected !")

        selected = cmds.ls(selection=True, long=True)
        if selected and self._replace_shape(item, selected):
            return

        manip_name = self._name.text()
        if not manip_name:
            raise RuntimeError("No name given !")

        new_manip = Manip(manip_name)
        new_manip.build(shape=item.name, scale=self.scale_factor)

        if cmds.nodeType(selected[0]) == "joint":
            new_manip.snap(selected[0])
    
    def _replace_shape(self, item: ShapeItem, nodes: list) -> bool:
        replaced = False
        for node in nodes:
            shapes = cmds.listRelatives(node, shapes=True, fullPath=True, noIntermediate=True)
            if not shapes:
                continue
            cmds.delete(shapes)
            new_shape = Shape.load(item.name)
            new_shape.parent = node
            new_shape.build(scale=self.scale_factor)
            replaced = True

        return replaced
        

class ShapeSettings(QtWidgets.QWidget):

    scaleFactorChanged = QtCore.Signal(float)
    
    def __init__(self, parent: QtWidgets.QWidget = None):
        super().__init__(parent)

        self._layout = QtWidgets.QVBoxLayout(self)
        self._layout.setSpacing(2)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setAlignment(QtCore.Qt.AlignTop)

        self._init_color()
        self._init_settings()

    def _init_color(self):
        color_widget = ColorWidget()
        self._layout.addWidget(color_widget)

    def _init_settings(self):
        widget = QtWidgets.QWidget(self)
        self._layout.addWidget(widget)

        layout = QtWidgets.QVBoxLayout(widget)
        layout.setSpacing(3)
        layout.setContentsMargins(0, 0, 0, 0)

        self._scale_factor = HSlider("Scale Factor", 0, 100, self)
        self._scale_factor.set_value(1.0)
        self._scale_factor.valueChanged.connect(self._scale_shape)
        layout.addWidget(self._scale_factor)
    
        self._line_width = HSlider("Line Width", 1, 10, self)
        self._line_width.valueChanged.connect(self._set_line_width)
        layout.addWidget(self._line_width)
    
    def _scale_shape(self, value):
        self.scaleFactorChanged.emit(value)

    def _set_line_width(self, value):
        shapes = cmds.ls(selection=True, long=True, type="nurbsCurve")
        transforms = cmds.ls(selection=True, long=True, type="transform")
        for t in transforms:
            children = cmds.listRelatives(t, children=True, fullPath=True, type="nurbsCurve") or []
            shapes.extend(children)
        
        [cmds.setAttr(f"{s}.lineWidth", value) for s in shapes]


class ShapeBasicUI(QtWidgets.QDialog):

    SINGLETON = None
    
    def __init__(self, parent=None):

        if ShapeBasicUI.SINGLETON is not None:
            ShapeBasicUI.SINGLETON.close()
        ShapeBasicUI.SINGLETON = self

        if not parent:
            parent = utils.main_window()
        super().__init__(parent)
        
        self._layout = QtWidgets.QHBoxLayout(self)
        self._layout.setSpacing(2)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self._shape_view = ShapeView()
        self._layout.addWidget(self._shape_view)

        self._shape_settings = ShapeSettings()
        self._shape_settings.scaleFactorChanged.connect(self._on_scale_changed)
        self._layout.addWidget(self._shape_settings)

    def _on_scale_changed(self, value):
        self._shape_view.scale_factor = value

