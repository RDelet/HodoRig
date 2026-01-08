from __future__ import annotations

import json
from pathlib import Path
import re

try:
    from PySide2 import QtCore, QtGui
    from PySide2.QtCore import QRegExp
except:
    from PySide6 import QtCore, QtGui
    from PySide6.QtCore import QRegularExpression as QRegExp

from maya import cmds

from ...Core import file
from ...Core.logger import log
from .. import utils as uiUtils


MAYA_VERSION = cmds.about(version=True)
DEFAULT_COLOR = "white"
DEFAULT_FONT_FAMILY = "Courier New"
RULES_FILE_PATH = Path(__file__).parent.parent / "Configs" / "syntaxRules.json"
WINDOWS_PATH_PATTERN = r"(?P<drive>[A-Za-z]:)[/\\](?P<path>[^:*?\"<>|\s]+\.[\w]+)"
LINE_NUMBER_PATTERN = r"(?i)line\s(?P<line_number>\d+)"


class SyntaxRule:

    def __init__(self, pattern: str, color: str = None, background_color: str = None,
                 font_family: str = None, italic: bool = False, underline: bool = False):
        self.pattern = QRegExp(pattern)
        self.color = color
        self.background_color = background_color
        self.font_family = font_family or DEFAULT_FONT_FAMILY
        self.italic = italic or False
        self.underline = underline or False
        
        self.format = QtGui.QTextCharFormat()
        self.font = QtGui.QFont()
    
        self.setup()

    def setup(self):
        self.format.setForeground(QtGui.QColor(self.color or DEFAULT_COLOR))
        self.font.setFamily(self.font_family)

        if self.background_color:
            self.format.setBackground(QtGui.QColor(self.background_color))
        if self.underline:
            self.format.setUnderlineStyle(QtGui.QTextCharFormat.SingleUnderline)

    @classmethod
    def from_dict(cls, rule_dict):
        return SyntaxRule(rule_dict.get("pattern", ""),
                          rule_dict.get("color"),
                          rule_dict.get("background_color"),
                          rule_dict.get("font_family"),
                          rule_dict.get("italic", False),
                          rule_dict.get("underline", False))

    def to_dict(self):
        return {"pattern": self.pattern,
                "color": self.color,
                "background_color": self.background_color,
                "font_family": self.font_family,
                "italic": self.italic,
                "underline": self.underline}


class SyntaxHighlighter(QtGui.QSyntaxHighlighter):

    def __init__(self, rules: list, document: QtGui.QTextDocument):
        super().__init__(document)
        self.rules = rules

    def highlightBlock(self, text):
        for rule in self.rules:
            if MAYA_VERSION < "2025":
                index = rule.pattern.indexIn(text)
                while index >= 0:
                    length = rule.pattern.matchedLength()
                    self.setFormat(index, length, rule.format)
                    index = rule.pattern.indexIn(text, index + length)
            else:
                iterator = rule.pattern.globalMatch(text)
                while iterator.hasNext():
                    match = iterator.next()
                    index = match.capturedStart()
                    length = match.capturedLength()
                    self.setFormat(index, length, rule.format)

            self.setCurrentBlockState(0)


class LinkFilter(QtCore.QObject):

    instance = None

    def __init__(self, parent=None):
        super().__init__(parent)

    @staticmethod
    def get_file_path_and_line_number(text):
        file_path, line_number = None, None

        match = re.search(WINDOWS_PATH_PATTERN, text)
        if match:
            file_path = match.group(0)
            line_match = re.search(LINE_NUMBER_PATTERN, text)
            if line_match:
                line_number = line_match.group("line_number")

        return file_path, line_number

    def eventFilter(self, obj, event):
        is_mouse_button = event.type() in [QtCore.QEvent.Type.MouseButtonPress]
        if is_mouse_button:
            is_ctrl_modifier = event.modifiers() == QtCore.Qt.ControlModifier
            if is_ctrl_modifier:
                cursor = obj.cursorForPosition(obj.mapFromGlobal(QtGui.QCursor().pos()))
                text = cursor.block().text()
                path, line_number = self.get_file_path_and_line_number(text)
                if line_number:
                    file.open_in_ide(path, line_number)
                else:
                    file.open_in_explorer(path)

                return True

        return super().eventFilter(obj, event)


def _get_rules() -> list:
    with open(RULES_FILE_PATH, "r") as f:
        data = json.load(f)

    return [SyntaxRule.from_dict(d) for k, d in data.items()]


# Je sépare en deux fonction pour niquer le evaldeffered qui ne fonctionne pas comme il faut...
def install_highlighter() -> bool:

    script_editor_output = uiUtils.script_editor_output_widget()
    if not script_editor_output:
        return False

    SyntaxHighlighter(_get_rules(), script_editor_output.document())

    return True


def install_linker() -> bool:

    script_editor_output = uiUtils.script_editor_output_widget()
    if not script_editor_output:
        return False

    instance = LinkFilter.instance
    if not instance:
        event_filter = LinkFilter()
        script_editor_output.installEventFilter(event_filter)
        LinkFilter.instance = event_filter
    
    return True
