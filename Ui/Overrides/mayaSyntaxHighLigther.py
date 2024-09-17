from PySide2 import QtWidgets

from ...Ui.Overrides.syntaxHighLigther import SyntaxHighLigther


class MayaSyntaxHighLigther(SyntaxHighLigther):

    kBaseName = "cmdScrollField"

    @classmethod
    def focus_changed_cb(cls, old_widget: QtWidgets.QWidget, new_widget: QtWidgets.QWidget):
        if new_widget:
            widget_name = new_widget.objectName()
            if cls.kBaseName and not widget_name.startswith(cls.kBaseName):
                return
            cls.add_on_all_control()

    @classmethod
    def add_on_all_control(cls):
        i = 1
        while True:
            widget = cls.add_on_widget(f"{cls.kBaseName}Reporter{i}")
            if not widget:
                break
            i += 1