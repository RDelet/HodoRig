from dataclasses import dataclass
import traceback
from typing import Optional

from PySide2.QtWidgets import QDialog, QHBoxLayout, QWidget, QLabel


@dataclass
class ErrorInfo:
    type: str
    message: str
    traceback: str
    cls_name: str
    function: str
    filename: str
    line: int


def collect_exception_info(exception):
    errors = []
    current = exception
    while current:
        tb = current.__traceback__
        cls_name, function_name, filename, lineno = None, None, None, None

        if tb is not None:
            while tb:
                frame = tb.tb_frame
                lineno = tb.tb_lineno
                code = frame.f_code
                function_name = code.co_name
                filename = code.co_filename

                if "self" in frame.f_locals:
                    cls_name = type(frame.f_locals["self"]).__name__

                tb = tb.tb_next  # Passe au cadre suivant

        error_info = ErrorInfo(type=type(current).__name__,
                               message=str(current),
                               traceback=''.join(traceback.format_exception(type(current), current, current.__traceback__)),
                               cls_name=cls_name,
                               function=function_name,
                               filename=filename,
                               line=lineno)
        errors.append(error_info)
        current = current.__cause__

    return errors


try:
    func_c()
except Exception as e:
    data = collect_exception_info(e)
    print(data[0].get("traceback"))


class ExceptionWidget(QDialog):
    
    def __init__(self, data: ErrorInfo, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._data = data
        
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(2)
        
        title = f"{self._data.type}: "
        if self._data.cls_name:
            title += f"{self._data.cls_name}.{self._data.function} line {self._data.line} | {self._data.message}"
        else:
            title += f"{self._data.function} line {self._data.filename} | {self._data.message}"
        title = QLabel(title, self)
