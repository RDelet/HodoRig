import os

from maya import cmds

from PySide2 import QtWidgets, QtGui

from HodoRig.Ui import utils
from HodoRig.Ui.colorWidget import ColorWidget
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


class ShapeView(QtWidgets.QListWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.update_content()
    
    @staticmethod
    def _get_shape() -> list:
        p = constants.kShapeDir
        return [ShapeItem(os.path.join(p, x)) for x in os.listdir(p)]
    
    def update_content(self):
        self.clear()
        [self.addItem(item) for item in self._get_shape()]


class ShapeNameWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self._layout = QtWidgets.QFormLayout(self)
        self._layout.setSpacing(1)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self._reset = QtWidgets.QLineEdit("RESET", self)
        self._manip = QtWidgets.QLineEdit("MANIP", self)
        self._name = QtWidgets.QLineEdit("Hodor", self)
        self._layout.addRow("Reset Prefix", self._reset)
        self._layout.addRow("Manip Prefix", self._manip)
        self._layout.addRow("Manip Name", self._name)
    
    @property
    def reset_prefix(self):
        return self._reset.text()
    
    @property
    def manip_prefix(self):
        return self._manip.text()
    
    @property
    def manip_name(self):
        return self._name.text()


class ShapeBasicUI(QtWidgets.QDialog):
    
    def __init__(self, parent=None):

        if not parent:
            parent = utils.main_window()
        super().__init__(parent)
        
        self._layout = QtWidgets.QVBoxLayout(self)
        self._layout.setSpacing(2)
        self._layout.setContentsMargins(1, 1, 1, 1)
    
        self._init_color()
        self._init_shapes()
       
    def _init_color(self):
        color_widget = ColorWidget()
        self._layout.addWidget(color_widget)
    
    def _init_shapes(self):
        widget = QtWidgets.QWidget(self)
        self._layout.addWidget(widget)

        layout = QtWidgets.QHBoxLayout(widget)
        layout.setSpacing(1)
        layout.setContentsMargins(0, 0, 0, 0)

        self._shape_view = ShapeView()
        layout.addWidget(self._shape_view)
        self._shape_view.itemDoubleClicked.connect(self._build_manip)

        self._shape_name = ShapeNameWidget()
        layout.addWidget(self._shape_name)
    
    def dump_shape(self):
        selected = cmds.ls(selection=True, long=True)
        if len(selected) > 1:
            raise RuntimeError("select one node !")
            
        file_name = self._name.text()
        if not file_name:
            raise RuntimeError("No name given !")
        
        shapes = self._get_shape()
        if file_name in shapes:
            raise RuntimeError(f"File {file_name}.{constants.kShapeExtension} already exists!")

        new_shape = Shape()
        new_shape.get_from_node(selected[0])
        new_shape.dump(file_name)

        self.update_content()
    
    def _build_manip(self, item=None):

        if not item:
            selected = self._shape_view.selectedItems()
            if selected:
                item = selected[0]
            else:
                raise RuntimeError("No item selected !")

        manip_name = self._name.text()
        if not manip_name:
            raise RuntimeError("No name given !")

        new_manip = Manip(manip_name)
        new_manip.build(shape=item.name)
