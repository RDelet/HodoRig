from maya import cmds

from PySide2 import QtWidgets

from HodoRig.Core import constants


class ColorButton(QtWidgets.QPushButton):
    
    def __init__(self, parent, color):
        super(ColorButton, self).__init__(parent)
        
        self.color = color
        self.setStyleSheet("background-color: rgb({0}, {1}, {2});".format(*self.color.rgb))


class ColorWidget(QtWidgets.QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(5)
        self.setLayout(layout)
        
        button_layout = None
        for i, color in enumerate(constants.kColors):
            if i % 5 == 0:
                button_layout = QtWidgets.QHBoxLayout()
                button_layout.setContentsMargins(0, 0, 0, 0)
                button_layout.setSpacing(2)
                layout.addLayout(button_layout)

            button = ColorButton(self, color)
            button.clicked.connect(self._set_color)
            button_layout.addWidget(button)
    
    def _set_color(self):
        color = self.sender().color
        selected = cmds.ls(selection=True, long=True, type='transform')
        shapes = cmds.listRelatives(selected, shapes=True, fullPath=True)
        for shape in shapes:
            cmds.setAttr('{0}.overrideEnabled'.format(shape), True)
            cmds.setAttr('{0}.overrideColor'.format(shape), color.maya_index)