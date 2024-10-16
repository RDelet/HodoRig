from PySide2 import QtWidgets
from shiboken2 import wrapInstance

from maya import OpenMayaUI


def error_dialog(parent: QtWidgets.QWidget, msg: str):
    widget = QtWidgets.QMessageBox(parent)
    widget.setIcon(QtWidgets.QMessageBox.Critical)
    widget.setWindowTitle("Error")
    widget.setText(msg)
    widget.setStandardButtons(QtWidgets.QMessageBox.Ok)
    widget.exec_()


def find_control(control_name: str, widget_cls: QtWidgets.QWidget = QtWidgets.QWidget) -> QtWidgets.QWidget:
    ptr = OpenMayaUI.MQtUtil.findControl(control_name)
    if not ptr:
        return
    
    return wrapInstance(int(ptr), widget_cls)


def main_window() -> QtWidgets.QWidget:
    ptr = OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(int(ptr), QtWidgets.QWidget)
