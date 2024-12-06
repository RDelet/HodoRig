from __future__ import annotations
from typing import Optional

try:
    from PySide2 import QtWidgets
except:
    from PySide6 import QtWidgets

from ...Ui import utils as uiUtils
from ...Ui.Overrides.syntaxHighLigther import SyntaxHighLigther


class MayaSyntaxHighLigther(SyntaxHighLigther):

    @classmethod
    def add_on_script_editor(cls) -> Optional[MayaSyntaxHighLigther]:
        script_editor_widget = uiUtils.find_control("scriptEditorPanel1Window")
        if not script_editor_widget:
            return

        output_widget = script_editor_widget.findChild(QtWidgets.QWidget, "cmdScrollFieldReporter1")
        if output_widget:
            return cls(output_widget)

    @classmethod
    def _on_focus_changed(cls):
        cls.add_on_script_editor()
    
    @classmethod
    def init_high_ligther(cls):
        app = QtWidgets.QApplication.instance()
        app.focusChanged.connect(MayaSyntaxHighLigther._on_focus_changed)
    
