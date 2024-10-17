# coding=ascii

import os
import textwrap
import traceback

try:
    from PySide2 import QtCore, QtGui, QtWidgets
except:
    from PySide6 import QtCore, QtGui, QtWidgets

from ..Helpers import quickScripts

from ..Core import constants
from ..Core.logger import log


class QuickScriptUiLite(QtWidgets.QWidget):
    
    SINGLETON = None

    def __init__(self, parent=None):
        super().__init__(parent)

        self._bg_color = [0.05, 0.05, 0.05, 0.6]
        self._asset_list_focus = False
        self._item_height = 30
        self._item_height_factor = 6
        self._width = 500
        self._height = 50
        self._x_offset = self._width
        self._y_offset = self._height * 0.5
        self.setFixedSize(self._width, self._height)

        self.__singleton()
        self.__set_ui()
        self.__exit_button()
        self.__search_field()
        self.__asset_list()
    
    def __singleton(self):
        if self.SINGLETON is not None:
            self.SINGLETON.close_window()
        self.SINGLETON = self
    
    def __set_ui(self):
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
    
    def __exit_button(self):
        qt_exit_button = QtWidgets.QPushButton(self)
        qt_exit_button.setFlat(True)
        qt_exit_button.setIcon(constants.kClose)
        qt_exit_button.setIconSize(QtCore.QSize(20, 20))
        qt_exit_button.move(5, 10)
        qt_exit_button.clicked.connect(self.close_window)
    
    def __search_field(self):
        self._text_field = QtWidgets.QLineEdit(self)
        self._text_field.setStyleSheet(textwrap.dedent("""
                                                         border: 1px solid rgb(35, 35, 35);
                                                         border-radius: 10px;
                                                         background-color: rgba(60, 60, 60, 153);
                                                         """))
        self._text_field.setFrame(False)
        self._text_field.setFixedSize(self._width - 55, 30)
        self._text_field.move(40, 10)
        self._text_field.textChanged.connect(self.__on_text_changed)

    def __asset_list(self):
        self._scripts_list = QtWidgets.QListView(self)
        self._scripts_list.setIconSize(QtCore.QSize(25, 25))
        self._scripts_list.move(40, 46)
        self._scripts_list.setFrameStyle(QtWidgets.QFrame.NoFrame)
        self._scripts_list.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self._scripts_list.setFixedSize(self._text_field.width(), self._item_height * self._item_height_factor)
        self._scripts_list.setStyleSheet(
            "background-color: rgba({0})".format(", ".join([str(255 * x) for x in self._bg_color])))

        self._model = QtGui.QStandardItemModel()
        self._scripts_list.setModel(self._model)
        self._scripts_list.hide()

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "{0}()".format(self.__class__.__name__)

    def __add_item(self, mod):
        item = QtGui.QStandardItem(constants.kPython, mod.kScriptName)
        item.setEditable(False)
        item.setToolTip(mod.__doc__.format(s_path=mod.__file__))
        self._model.appendRow(item)
        self._items.append(item)

    def __launch_script(self):
        selected_index = self._scripts_list.selectedIndexes()
        if not selected_index:
            return
        index = selected_index[0]

        name = index.data()
        if name not in self.__scripts:
            log.warning(f"Script {name} not found.")

        try:
            self.__scripts[name].main()
        except Exception as e:
            log.debug(traceback.format_exc())
            log.error(f"Error on launch scripts {name} !")

        self.close()

    def _clear_content(self):
        self._model.removeRows(0, self._model.rowCount())
        self._items = list()

    def _update_content(self, text: str = ""):
        quickScripts.retrieve()
        self.__scripts = quickScripts.get_scripts()

        for name, mod in list(self.__scripts.items()):
            if text.lower() in name.lower():
                self.__add_item(mod)
    
    def _resize_content(self):
        height = self._item_height * len(self._items)
        self._scripts_list.setFixedSize(self._scripts_list.width(), height)
        self.setFixedSize(self._width, self._height + height)

    def __on_text_changed(self):

        text = self._text_field.text()
        if text == "":
            self._scripts_list.hide()
            return

        self._scripts_list.show()
        
        self._clear_content()
        self._update_content(text)
        self._resize_content()

    def close_window(self):
        self.deleteLater()
        self.close()

    def closeEvent(self, event):
        self.close_window()
        event.accept()
        super().closeEvent(event)

    def mousePressEvent(self, event):
        qt_cursor_pos = event.pos()
        self._x_offset = qt_cursor_pos.x()
        self._y_offset = qt_cursor_pos.y()

    def mouseMoveEvent(self, event):
        self.move(event.globalX() - self._x_offset, event.globalY() - self._y_offset)

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Escape:
            self.close_window()
        elif key == QtCore.Qt.Key_Return or key == QtCore.Qt.Key_Enter:
            self.__launch_script()
        elif key == QtCore.Qt.Key_Up:
            if self._asset_list_focus is True:
                self._text_field.setFocus()
                self._asset_list_focus = False
                self._scripts_list.selectionModel().clearSelection()
        elif key == QtCore.Qt.Key_Down and self._asset_list_focus is False:
            self._asset_list_focus = True
            self._scripts_list.setFocus()
            current_index = self._scripts_list.selectionModel().currentIndex()
            if current_index is None:
                item = self._model.child(0)
                current_index = item.index()
            self._scripts_list.selectionModel().select(current_index, QtCore.QItemSelectionModel.Select)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        brush_color = QtGui.QColor.fromRgbF(self._bg_color[0],
                                               self._bg_color[1], 
                                               self._bg_color[2],
                                               self._bg_color[3])
        brush = QtGui.QBrush(brush_color)
        painter.setBrush(brush)

        pen_color = QtGui.QColor.fromRgbF(0.05, 0.05, 0.05, 0.7)
        pen = QtGui.QPen(pen_color)
        pen.setWidth(2)
        painter.setPen(pen)

        painter.drawRoundedRect(QtCore.QRect(5, 5, self._width - 10, self._height - 10), 15.0, 15.0)
