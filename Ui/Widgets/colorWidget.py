from maya import cmds
from maya.api import OpenMaya

try:
    from PySide2 import QtWidgets
except:
    from PySide6 import QtWidgets

from ...Helpers import color as Color
from ...Core.logger import log
from ...Nodes.node import Node
from ...Ui.Widgets.groupWidget import GroupWidget


class ColorButton(QtWidgets.QPushButton):
    
    def __init__(self, parent, color):
        super(ColorButton, self).__init__(parent)
        
        self.color = color
        self.setStyleSheet("background-color: rgb({0}, {1}, {2});".format(*self.color.rgb))


class ColorWidget(GroupWidget):
    
    def __init__(self, name: str = "Color",
                 button_size: int = 30, line_count: int = 5,
                 parent: QtWidgets.QWidget = None):
        super().__init__(name, parent=parent)
        
        self._button_size = button_size
        
        button_layout = None
        for i, color in enumerate(Color.kAll.values()):
            if i % line_count == 0:
                button_layout = QtWidgets.QHBoxLayout()
                button_layout.setContentsMargins(0, 0, 0, 0)
                button_layout.setSpacing(0)
                self.add_layout(button_layout)

            button = ColorButton(self, color)
            button.setFixedHeight(self._button_size)
            button.clicked.connect(self._set_color)
            button_layout.addWidget(button)

    def _set_color(self):
        color = self.sender().color
        selected = cmds.ls(selection=True, long=True)
        for node in selected:
            node = Node.get(node)
            if not node.has_fn(OpenMaya.MFn.kDagNode):
                continue
            color.apply_by_index(node)
