from PySide2 import QtWidgets
from shiboken2 import wrapInstance

from maya import OpenMayaUI


def find_control(control_name: str, widget_cls: QtWidgets.QWidget = QtWidgets.QWidget) -> QtWidgets.QTextEdit:
    ptr = OpenMayaUI.MQtUtil.findControl(control_name)
    if not ptr:
        return
    
    return wrapInstance(int(ptr), widget_cls)