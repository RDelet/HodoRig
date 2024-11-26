import traceback
from typing import Optional

from PySide2.QtWidgets import (
    QDialog, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QWidget, QMenu, QLabel, QPushButton, QHBoxLayout, QTreeWidgetItemIterator, QTextEdit
)
from PySide2.QtGui import QColor
from PySide2.QtCore import Qt


def func_a():
    raise RuntimeError('Hodor')

def func_b():
    try:
        func_a()
    except Exception as e:
        raise TypeError('Groot') from e

def func_c():
    try:
        func_b()
    except Exception as e:
        raise NotImplementedError('Kapouet') from e


class CustomTreeItem(QTreeWidgetItem):
    """
    Un item personnalisé pour afficher les erreurs sous forme de widgets.
    """
    def __init__(self, error, parent=None):
        super().__init__(parent)
        self.error = error
        self.setText(0, f"{error['type']}: {error['message']}")

    def show_traceback(self, parent_widget):
        """
        Affiche une boîte de dialogue avec la traceback complète.
        """
        traceback_dialog = QDialog(parent_widget)
        traceback_dialog.setWindowTitle(f"Traceback: {self.error['type']}")
        traceback_dialog.setGeometry(200, 200, 600, 400)

        layout = QVBoxLayout(traceback_dialog)

        traceback_text = QTextEdit()
        traceback_text.setReadOnly(True)
        traceback_text.setText(self.error['traceback'])
        layout.addWidget(traceback_text)

        close_button = QPushButton("Close")
        close_button.clicked.connect(traceback_dialog.accept)
        layout.addWidget(close_button)

        traceback_dialog.exec_()


class ErrorViewer(QDialog):

    def __init__(self, exception: Exception, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("Error Viewer")
        self.setGeometry(100, 100, 800, 600)

        self._errors = self._collect(exception)

        self._init_layout()
        self._init_view()
        self._update_view()
    
    def _init_layout(self):
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(2)

    def _init_view(self):
        self.error_tree = QTreeWidget()
        self.error_tree.setHeaderLabels(["Exception Details"])
        self.error_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.error_tree.customContextMenuRequested.connect(self._on_context_menu)
        self._layout.addWidget(self.error_tree)


def collect_exception_info(exception):
    """
    Récupère des informations sur la classe et la fonction où l'exception a été levée.
    """
    tb = exception.__traceback__
    while tb is not None:
        frame = tb.tb_frame  # Accède au cadre actuel
        lineno = tb.tb_lineno  # Ligne où l'exception s'est produite
        code = frame.f_code  # Obtenir les informations du code

        # Détails de la fonction
        function_name = code.co_name
        filename = code.co_filename

        # Vérifie si "self" est dans les variables locales pour identifier la classe
        cls_name = None
        if "self" in frame.f_locals:
            cls_name = type(frame.f_locals["self"]).__name__

        return {
            "filename": filename,
            "line": lineno,
            "function": function_name,
            "class": cls_name,
        }

        tb = tb.tb_next  # Passe au cadre suivant

def _collect(exception):
    errors = []
    current = exception
    while current:
        errors.append({
            "type": type(current).__name__,
            "message": str(current),
            "traceback": cls._get_traceback(current)
        })
        current = current.__cause__
    return errors

def _get_traceback(exception: Exception) -> str:
    return ''.join(traceback.format_exception(type(exception), exception, exception.__traceback__))

    def _update_view(self):
        parent_item = None
        for error in self._errors:
            item = CustomTreeItem(error)
            if parent_item is None:
                self.error_tree.addTopLevelItem(item)
            else:
                parent_item.addChild(item)

            parent_item = item

    def _on_context_menu(self, position):
        """
        Gère le clic droit sur les items pour afficher un menu contextuel.
        """
        item = self.error_tree.itemAt(position)
        if isinstance(item, CustomTreeItem):
            menu = QMenu(self)
            action_show_traceback = menu.addAction("Show Traceback")
            action = menu.exec_(self.error_tree.viewport().mapToGlobal(position))
            if action == action_show_traceback:
                item.show_traceback(self)


try:
    func_c()
except Exception as e:
    viewer = ErrorViewer(e)
    viewer.show()