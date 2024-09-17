import os
from functools import partial

from maya import cmds
from maya.api import OpenMaya

from PySide2 import QtCore, QtWidgets

from ..Core import constants, file
from ..Nodes.node import Node
from ..Nodes._shape import _Shape
from ..Nodes.manip import Manip
from ..Ui import utils
from ..Ui.Widgets.colorWidget import ColorWidget
from ..Ui.Widgets.hSlider import HSlider
from ..Ui.Widgets.groupWidget import GroupWidget


class ShapeItem(QtWidgets.QListWidgetItem):

    def __init__(self, path, *args, **kwargs):

        self.path = path
        self.name = os.path.split(path)[-1].split(".")[0]

        super().__init__(self.name, *args, **kwargs)
    
    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return self.name
    
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
        slider = HSlider("Scale", -100, 100, self)
        slider.value = 1.0
        slider.valueChanged.connect(partial(self._do, normalize=True))
        self.add_widget(slider)

    def _do(self, value, normalize=False):
        if value >= 0:
            value = max(1e-3, value)
        if value <= 0:
            value = min(-1e-3, value)

        shapes = cmds.ls(selection=True, long=True, type="shape") or []
        transforms = cmds.ls(selection=True, long=True, type="transform") or []
        children = cmds.listRelatives(transforms, shapes=True, fullPath=True) or []
        shapes = list(set(shapes + children))

        for node in shapes:
            shape = Node.get_node(node)
            shape.scale(value, normalize=normalize)


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
    def get_shape_path(file_name: str) -> str:
        if "." not in file_name:
            file_name = f"{file_name}.{constants.kShapeExtension}"
        return os.path.join(constants.kShapeDir, file_name)
    
    @classmethod
    def get_shapes(cls) -> list:
        p = constants.kShapeDir
        return [ShapeItem(cls.get_shape_path(x)) for x in os.listdir(p)]
    
    def update_content(self):
        self._list_view.clear()
        [self._list_view.addItem(item) for item in self.get_shapes()]
    
    def dump_shape(self):
        selected = cmds.ls(selection=True, long=True)
        if len(selected) > 1:
            raise RuntimeError("select one node !")
        
        node = Node.get_node(selected[0])
        if not node.has_fn(OpenMaya.MFn.kTransform):
            raise RuntimeError("Select transform node !")
    
        shapes = node.shapes
        if len(shapes) == 0:
            raise RuntimeError(f"No shape found under {node.name} !")

        file_name, valid = QtWidgets.QInputDialog.getText(self, 'File Name', 'Give file name')
        if not valid:
            return
        if not file_name:
            raise RuntimeError("No name given !")

        if file_name in self.get_shapes():
            raise RuntimeError(f"File {file_name}.{constants.kShapeExtension} already exists!")

        data = []
        for shape in node.shapes:
            data.append(shape.to_dict())
        file.dump_json(data, self.get_shape_path(file_name))


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
        name = item.name if not txt else txt
        new_manip = Manip()
        new_manip.build(name, shape=item.name, scale=self._scale.value)

        if selected and cmds.nodeType(selected[0]) == "joint":
            new_manip.snap(selected[0])
    
    def _replace_shape(self, item: ShapeItem, nodes: list) -> bool:
        replaced = False
        for node in nodes:
            shapes = cmds.listRelatives(node, shapes=True, fullPath=True, noIntermediate=True)
            if not shapes:
                continue
            cmds.delete(shapes)
            _Shape.load(item.name, Node.get_node(node).object)
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

