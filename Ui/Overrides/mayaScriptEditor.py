from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
import re
import traceback
from typing import Optional

try:
    from PySide2 import QtCore, QtGui
    from PySide2.QtCore import QRegExp
except:
    from PySide6 import QtCore, QtGui
    from PySide6.QtCore import QRegularExpression as QRegExp

from maya import cmds

from ...Core import constants, file
from ...Core.logger import log
from .. import utils as uiUtils


DEFAULT_COLOR = "white"
DEFAULT_FONT_FAMILY = "Courier New"
RULES_FILE_PATH = Path(__file__).parent.parent / "Configs" / "syntaxRules.json"
WINDOWS_PATH_PATTERN = r"(?P<drive>[A-Za-z]:)[/\\](?P<path>[^:*?\"<>|\s]+\.[\w]+)"
LINE_NUMBER_PATTERN = r"(?i)line\s(?P<line_number>\d+)"


@dataclass
class SyntaxRule:

    pattern: str
    color: Optional[str] = None
    background_color: Optional[str] = None
    font_family: Optional[str] = None
    italic: bool = False
    underline: bool = False
    
    format: QtGui.QTextCharFormat = field(init=False, repr=False)
    font: QtGui.QFont = field(init=False, repr=False)
    
    def __post_init__(self):
        self.pattern = QRegExp(self.pattern)
        self.font_family = self.font_family or DEFAULT_FONT_FAMILY
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


class SyntaxHighlighter(QtGui.QSyntaxHighlighter):

    def __init__(self, rules: list, document: QtGui.QTextDocument):
        super().__init__(document)
        self.rules = rules
        self._highlight_func = self.__old if constants.IS_OLD_MAYA else self.__new

    def highlightBlock(self, text):
        for rule in self.rules:
            self._highlight_func(rule, text)
        self.setCurrentBlockState(0)
    
    def __old(self, rule: SyntaxRule, text: str):
        index = rule.pattern.indexIn(text)
        while index >= 0:
            length = rule.pattern.matchedLength()
            self.setFormat(index, length, rule.format)
            index = rule.pattern.indexIn(text, index + length)

    def __new(self, rule: SyntaxRule, text: str):
        iterator = rule.pattern.globalMatch(text)
        while iterator.hasNext():
            match = iterator.next()
            index = match.capturedStart()
            length = match.capturedLength()
            self.setFormat(index, length, rule.format)


class LinkFilter(QtCore.QObject):

    instance = None

    def __init__(self, parent=None):
        super().__init__(parent)

    @staticmethod
    def get_file_path_and_line_number(text):
        match = re.search(WINDOWS_PATH_PATTERN, text)
        if not match:
            return None, None
        
        file_path = match.group(0)
        line_match = re.search(LINE_NUMBER_PATTERN, text)
        line_number = line_match.group("line_number") if line_match else None
        
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

    return [SyntaxRule(**d) for k, d in data.items()]


def install() -> bool:
    script_editor_output = uiUtils.script_editor_output_widget()
    if not script_editor_output:
        return False

    try:
        SyntaxHighlighter(_get_rules(), script_editor_output.document())
        instance = LinkFilter.instance
        if not instance:
            event_filter = LinkFilter()
            script_editor_output.installEventFilter(event_filter)
            LinkFilter.instance = event_filter
    except Exception:
        log.debug(traceback.format_exc())
        log.error("Error on install syntax highlighter !")
        return False
    
    return True