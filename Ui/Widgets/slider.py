from __future__ import annotations

from typing import Optional

try:
    from PySide2 import QtCore, QtGui, QtWidgets
except:
    from PySide6 import QtCore, QtGui, QtWidgets


class Slider(QtWidgets.QSlider):

    isPressed = QtCore.Signal()
    isReleased = QtCore.Signal()

    class __Undo(QtWidgets.QUndoCommand):

        def __init__(self, widget, old_value, new_value):
            super().__init__(str(widget))
            self.widget = widget
            self.old_value = old_value
            self.new_value = new_value

        def undo(self):
            self.widget.setValue(self.old_value)

        def redo(self):
            self.widget.setValue(self.new_value)

    def __init__(self, min_value: int, max_value: int, parent: Optional[QtWidgets.QWidget] = None,
                 undo_stack: Optional[QtWidgets.QUndoStack] = None, factor: float = 1.0):
        super().__init__(QtCore.Qt.Horizontal, parent)
        self.undo_stack = undo_stack
        self.setRange(min_value, max_value)
        self.setFixedHeight(25)

        self.bg_color = QtGui.QColor("#EEEEEE")
        self.fg_color_enable = QtGui.QColor("#405C7A")
        self.fg_color_disable = QtGui.QColor("#757E8A")
        self.text_color = QtGui.QColor("#101D2B")

        self.lock_value = None
        self.__current_value = None
        self._factor = factor

    def mousePressEvent(self, event):
        self.__current_value = self.value()
        self.isPressed.emit()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self.__current_value is not None:
            undo = self.__Undo(self, self.__current_value, self.value())
            self.undo_stack.push(undo)
            self.__current_value = None
        self.isReleased.emit()
        super().mousePressEvent(event)

    def sliderChange(self, change: QtWidgets.QSlider.SliderChange):
        if change == QtWidgets.QSlider.SliderValueChange and self.lock_value is not None:
            self.setValue(min(self.value(), self.lock_value))
        super().sliderChange(change)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        slider_rect = self.rect()
        handle_pos = self.value() / self.maximum()
        # Background
        painter.setBrush(QtGui.QBrush(self.bg_color))
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRect(slider_rect)
        # Foreground
        filled_width = int(handle_pos * slider_rect.width())
        painter.setBrush(QtGui.QBrush(self.fg_color_enable if self.isEnabled() else self.fg_color_disable))
        painter.drawRect(0, 0, filled_width, slider_rect.height())
        # Text
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.setPen(self.text_color)
        painter.drawText(slider_rect, QtCore.Qt.AlignCenter, str(self.value() / self._factor))

        painter.end()

    def sizeHint(self):
        return QtCore.QSize(200, 20)