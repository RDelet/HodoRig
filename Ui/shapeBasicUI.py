import os
from functools import partial

from maya import cmds
from maya.api import OpenMaya

from PySide2 import QtCore, QtWidgets

from HodoRig.Core import constants, utils as mayaUtils
from HodoRig.Core.nameBuilder import NameBuilder
from HodoRig.Core.logger import log
from HodoRig.Nodes.manip import Manip
from HodoRig.Builders import shape
from HodoRig.Ui import utils
from HodoRig.Ui.Widgets.colorWidget import ColorWidget
from HodoRig.Ui.Widgets.hSlider import HSlider
from HodoRig.Ui.Widgets.groupWidget import GroupWidget


class ShapeItem(QtWidgets.QListWidgetItem):

    def __init__(self, path, *args, **kwargs):

        self.path = path
        self.name = os.path.split(path)[-1].split(".")[0]

        super().__init__(self.name, *args, **kwargs)
    
    @property
    def icon(self) -> str:
        dir, _ = os.path.split(self.path)
        return os.path.join(dir, f"{self.name}.{constants.kIconExtension}")


class ScaleWidget(GroupWidget):

    def __init__(self, name: str = "Scale", parent: QtWidgets.QWidget = None):
        super().__init__(name, parent=parent)

        self._init_buttons()
        self._init_slider()
    

    def _init_buttons(self):
        widget = QtWidgets.QWidget(self)
        self.add_widget(widget)

        layout = QtWidgets.QHBoxLayout(widget)
        layout.setSpacing(2)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(QtCore.Qt.AlignLeft)

        for value in [-1.0, 0.25, 0.5, 0.75, 1.5, 2.0, 5.0, 10.0]:
            button = QtWidgets.QPushButton(str(value), widget)
            button.setFixedWidth(30)
            button.clicked.connect(partial(self._do, value))
            layout.addWidget(button)
    
    def _init_slider(self):
        slider = HSlider("Scale", 0.1, 100, self)
        slider.value = 1.0
        slider.valueChanged.connect(partial(self._do, relative=False))
        self.add_widget(slider)

    def _do(self, value, relative=True):
        shapes = cmds.ls(selection=True, long=True, type="shape") or []
        transforms = cmds.ls(selection=True, long=True, type="transform") or []
        children = cmds.listRelatives(transforms, shapes=True, fullPath=True) or []
        shapes = list(set(shapes + children))
        cmds.scale(value, value, value, shapes, relative=relative)


class ShapeView(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self._layout = QtWidgets.QVBoxLayout(self)
        self._layout.setSpacing(2)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self._list_view = QtWidgets.QListWidget(self)
        self._list_view.itemDoubleClicked.connect(self._build_manip)
        self._layout.addWidget(self._list_view)

        self._settings()

        self._save_shape = QtWidgets.QPushButton("Save Shape", self)
        self._layout.addWidget(self._save_shape)
        self._save_shape.clicked.connect(self.dump_shape)

        self.update_content()
    
    def _settings(self):
        widget = QtWidgets.QWidget(self)
        self._layout.addWidget(widget)

        layout = QtWidgets.QFormLayout(widget)
        layout.setSpacing(2)
        layout.setContentsMargins(0, 0, 0, 0)

        self._name = QtWidgets.QLineEdit("", self)
        layout.addRow("Manip Name", self._name)

        self._scale = HSlider("", 0, 100, self)
        self._scale.value = 1.0
        layout.addRow("Scale Factor", self._scale)
    
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

        new_shape = shape.Shape()
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

        txt = self._name.text()
        manip_name = NameBuilder.from_name(item.name if not txt else txt)
        new_manip = Manip(manip_name)
        new_manip.build(shape=item.name, scale=self._scale.value)

        if selected and cmds.nodeType(selected[0]) == "joint":
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
    
    def __init__(self, parent: QtWidgets.QWidget = None):
        super().__init__(parent)

        self._layout = QtWidgets.QVBoxLayout(self)
        self._layout.setSpacing(2)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setAlignment(QtCore.Qt.AlignTop)

        self._init_color()
        self._init_scale()

    def _init_color(self):
        widget = ColorWidget()
        self._layout.addWidget(widget)

        self._line_width = HSlider("Line Width", 1, 10, self)
        self._line_width.valueChanged.connect(self._set_line_width)
        widget.add_widget(self._line_width)
    
    def _init_scale(self):
        widget = ScaleWidget()
        self._layout.addWidget(widget)

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
        self._layout.addWidget(self._shape_settings)

