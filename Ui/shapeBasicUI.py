import os

from maya import cmds

from PySide2 import QtWidgets, QtGui

from HodoRig.Ui import utils
from HodoRig.Core import constants
from HodoRig.Builders.shape import Shape
from HodoRig.Nodes.manip import Manip


class ShapeView(QtWidgets.QTreeView):

    def __init__(self, parent=None):
        super().__init__(parent)
    
    def _update_content(self):
        self.clear()
        for shape in self._get_shape():
            item = QtGui.QStandardItem(shape)
            self.model.appendRow(item)


class ShapeBasicUI(QtWidgets.QDialog):
    
    def __init__(self, parent=None):

        if not parent:
            parent = utils.main_window()
        super().__init__(parent)
        
        self._layout = QtWidgets.QVBoxLayout(self)
        self._layout.setSpacing(2)
        self._layout.setContentsMargins(1, 1, 1, 1)
    
        self._build_ui()
        self._update_content()
       
    def _build_ui(self):
        self._shapes = QtWidgets.QComboBox(self)
        self._layout.addWidget(self._shapes)
        
        self._name = QtWidgets.QLineEdit(self)
        self._layout.addWidget(self._name)
        
        build_button = QtWidgets.QPushButton("Build Manip", self)
        self._layout.addWidget(build_button)
        build_button.clicked.connect(self.build_manip)
        
        dump_selected = QtWidgets.QPushButton("Save Shape", self)
        self._layout.addWidget(dump_selected)
        dump_selected.clicked.connect(self.dump_shape)

        # shape_view = ShapeView()
        # self._layout.addWidget(shape_view)
    
    def _update_content(self):
        self._shapes.clear()
        self._shapes.addItems(self._get_shape())
    
    @staticmethod
    def _get_shape() -> list:
        return [x.split(".")[0] for x in os.listdir(constants.kShapeDir)]
    
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

        self._update_content()
    
    def build_manip(self):
        manip_name = self._name.text()
        if not manip_name:
            raise RuntimeError("No name given !")

        new_manip = Manip(manip_name)
        new_manip.build(shape=self._shapes.currentText())
