try:
    from PySide2 import QtWidgets
    from shiboken2 import wrapInstance
except:
    from PySide6 import QtWidgets
    from shiboken6 import wrapInstance


from maya import cmds, OpenMayaUI as omui


def error_dialog(parent: QtWidgets.QWidget, msg: str):
    widget = QtWidgets.QMessageBox(parent)
    widget.setIcon(QtWidgets.QMessageBox.Critical)
    widget.setWindowTitle("Error")
    widget.setText(msg)
    widget.setStandardButtons(QtWidgets.QMessageBox.Ok)
    widget.exec_()


def find_control(control_name: str, widget_cls: QtWidgets.QWidget = QtWidgets.QWidget) -> QtWidgets.QWidget:
    ptr = omui.MQtUtil.findControl(control_name)
    if not ptr:
        return
    
    return wrapInstance(int(ptr), widget_cls)


def main_window() -> QtWidgets.QWidget:
    ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(ptr), QtWidgets.QWidget)


def script_editor_output_widget() -> QtWidgets.QPlainTextEdit:
    cmds.ScriptEditor()
    i = 0
    while i < 1000:
        ptr = omui.MQtUtil.findControl(f"cmdScrollFieldReporter{i}")   
        if ptr: 
            return wrapInstance(int(ptr), QtWidgets.QPlainTextEdit)
        i += 1