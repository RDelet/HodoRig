from __future__ import annotations

import json
from typing import Optional

try:
    from PySide2.QtWidgets import (
        QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
        QPushButton, QInputDialog, QFileDialog, QMessageBox, QComboBox
    )
    from PySide2.QtWidgets import QAction
    from PySide2.QtCore import Signal
    from shiboken2 import wrapInstance
except:
    from PySide6.QtWidgets import (
        QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
        QPushButton, QInputDialog, QFileDialog, QMessageBox, QComboBox
    )
    from PySide6.QtGui import QAction
    from PySide6.QtCore import Signal
    from shiboken6 import wrapInstance

from maya.OpenMayaUI import MQtUtil


class JsonEncoder(json.JSONEncoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__indentation_level = 0

    def __convert_list(self, o: list | tuple) -> str:
        output = [self.encode(el) for el in o]
        return '[{0}]'.format(", ".join(output))
    
    def __convert_dict(self, o: dict) -> str:
        if not o:
            return "{}"
        
        self.__indentation_level += 1
        output = []
        for k, v in o.items():
            output.append('{0}{1}: {2}'.format(self.indent_str, json.dumps(k), self.encode(v)))
        self.__indentation_level -= 1
        if self.indent:
            return "{\n" + ",\n".join(output) + "\n" + self.indent_str + "}"
        else:
            return '{' + ", ".join(output) + '}'

    def encode(self, o: list | tuple | dict) -> str:
        if isinstance(o, (list, tuple)):
            return self.__convert_list(o)
        elif isinstance(o, dict):
            return self.__convert_dict(o)
        else:
            return json.dumps(o)

    def iterencode(self, o, **kwargs):
        return self.encode(o)

    @property
    def indent_str(self):
        return " " * self.__indentation_level * self.indent if self.indent else ''


class ComboBoxWidget(QWidget):
    changed = Signal()

    def __init__(self, items: list):
        super().__init__()
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.layout.setSpacing(1)

        self.combo = QComboBox()
        self.combo.addItems(items)
        self.layout.addWidget(self.combo)

        self.combo.currentIndexChanged.connect(self.on_selection_changed)

    def on_selection_changed(self):
        self.changed.emit()

    @property
    def value(self):
        return self.combo.currentIndex()
    
    @property
    def current_text(self):
        return self.combo.currentText()
    
    def set_current_text(self, text: str):
        index = self.combo.findText(text)
        if index >= 0:
            self.combo.setCurrentIndex(index)


class CorrectionApp(QMainWindow):
    def __init__(self, file: Optional[str] = None, parent: Optional[QWidget] = None):
        if parent is None:
            parent = wrapInstance(int(MQtUtil.mainWindow()), QWidget)
        super().__init__(parent)

        self.setWindowTitle("Correction des Travaux")
        self.setGeometry(100, 100, 800, 600)

        self._file = file

        self._init_menu()
        self._init_master_widget()
        self._init_table()
        self._init_barem()
        if self._file:
            self.update_content()
    
    def _init_master_widget(self):
        self.master_layout = QVBoxLayout()
        self.master_layout.setContentsMargins(2, 2, 2, 2)
        self.master_layout.setSpacing(0)

        container = QWidget()
        container.setLayout(self.master_layout)
        self.setCentralWidget(container)

    def _init_menu(self):
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("File")

        self.load_action = QAction("Load file", self)
        self.load_action.triggered.connect(self._load_file)
        self.file_menu.addAction(self.load_action)

    def _init_table(self):
        self.table = QTableWidget()
        self.table.setRowCount(0)
        self.table.setColumnCount(0)
        self.master_layout.addWidget(self.table)

        self.add_column_button = QPushButton("Ajouter une colonne")
        self.add_column_button.clicked.connect(self.ajouter_colonne)
        self.master_layout.addWidget(self.add_column_button)

        self.add_student_button = QPushButton("Ajouter un étudiant")
        self.add_student_button.clicked.connect(self.ajouter_etudiant)
        self.master_layout.addWidget(self.add_student_button)
    
    def _init_barem(self):
        data = self._read_json(self._file)
        self._barem = data.get("barem", {})

    def _compute_totals(self):
        for row in range(1, self.table.rowCount()):
            total = 10
            for col in range(1, self.table.columnCount() - 1):
                widget: ComboBoxWidget = self.table.cellWidget(row, col)
                if not widget:
                    continue
                bareme_item = self.table.item(0, col)
                bareme = 0
                if bareme_item is not None:
                    try:
                        bareme = float(bareme_item.text())
                    except ValueError:
                        pass
                total += bareme * self._barem["factor"][widget.value]

            self.table.setItem(row, self.table.columnCount() - 2, QTableWidgetItem(str(total)))

        self.sauvegarder_donnees()
        self.table.resizeRowsToContents()

    def _create_combo(self, row, col):
        combo_widget = ComboBoxWidget(list(self._barem["name"].keys()))
        combo_widget.changed.connect(self._compute_totals)
        self.table.setCellWidget(row, col, combo_widget)
        self.table.resizeColumnsToContents()

    def ajouter_colonne(self):
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Erreur", "Add student before !")
            return

        current_columns = self.table.columnCount()

        task, ok = QInputDialog.getText(self, "New task", "Task Name:")
        if not ok or not task:
            task = f"Task {current_columns - 1}"
        self.table.insertColumn(current_columns - 1)
        self.table.setHorizontalHeaderItem(current_columns - 1, QTableWidgetItem(task))

        bareme = 0.0
        item_bareme = QTableWidgetItem(str(bareme))
        self.table.setItem(0, current_columns - 1, item_bareme)
        for row in range(1, self.table.rowCount()):
            self._create_combo(row, current_columns - 1)

        self.sauvegarder_donnees()
        self.table.resizeColumnsToContents()

    def ajouter_etudiant(self):
        nom_etudiant, ok = QInputDialog.getText(self, "New student", "Student Name:")
        if not ok or not nom_etudiant:
            return

        current_rows = self.table.rowCount()
        if current_rows == 0:
            self.table.setRowCount(1)
            self.table.setColumnCount(2)
            self.table.setHorizontalHeaderLabels(["Name", "Totals"])

        self.table.insertRow(current_rows)
        self.table.setItem(current_rows, 0, QTableWidgetItem(nom_etudiant))
        for col in range(1, self.table.columnCount() - 2):
            self._create_combo(current_rows, col)

        self.add_column_button.setEnabled(True)
        self.add_student_button.setEnabled(True)
        self._compute_totals()

        self.table.resizeColumnsToContents()

    def _read_json(self, file_path: str):
        try:
            with open(file_path, 'r', encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible to load file : {str(e)}")

    def _load_file(self):
        self._file, _ = QFileDialog.getOpenFileName(self, "Open Json file", "", "File JSON (*.json)")
        if not self._file:
            return
        self.update_content()
            
    def update_content(self):
        data = self._read_json(self._file)
        taches = data.get("taches", [])
        etudiants = data.get("etudiants", [])

        # Configurer le nombre de colonnes en ajoutant une colonne pour les commentaires
        self.table.setRowCount(0)
        self.table.setColumnCount(len(taches) + 3)  # Ajouter 3 : Nom, Totaux, et Commentaires
        task_headers = [task["name"] for task in taches]
        self.table.setHorizontalHeaderLabels(["Nom"] + task_headers + ["Total", "Commentaires"])
        self.table.setRowCount(len(etudiants) + 1)
    
        # Insérer les notes des tâches (première ligne)
        for i, task in enumerate(taches, start=1):
            item = QTableWidgetItem(str(task["note"]))
            self.table.setItem(0, i, item)
    
        # Remplir la table avec les étudiants, leurs notes et leurs commentaires
        for row, etudiant in enumerate(etudiants, start=1):
            nom = etudiant["name"]
            notes = etudiant["notes"]
            if len(notes) < len(taches):
                for i in range((len(taches) - len(notes))):
                    notes.append(list(self._barem.get("name").keys())[0])
            commentaires = etudiant.get("commentaires", "")
    
            # Nom de l'étudiant
            self.table.setItem(row, 0, QTableWidgetItem(nom))
    
            # Insérer les combo box pour chaque tâche
            for col, note in enumerate(notes, start=1):
                widget = ComboBoxWidget(list(self._barem["name"].keys()))
                widget.changed.connect(self._compute_totals)
                widget.set_current_text(note)
                self.table.setCellWidget(row, col, widget)
    
            # Colonne des commentaires
            commentaire_item = QTableWidgetItem(commentaires)
            self.table.setItem(row, self.table.columnCount() - 1, commentaire_item)
    
        # Calculer les totaux
        self._compute_totals()
        self.table.resizeColumnsToContents()
        self.table.adjustSize()

    def sauvegarder_donnees(self):
        if not self._file:
            return
        
        data = {"taches": [], "barem": self._barem, "etudiants": []}
    
        # Extraire les informations des tâches
        for i in range(1, self.table.columnCount() - 2):
            task_name = self.table.horizontalHeaderItem(i).text()
            note_item = self.table.item(0, i)
            note = float(note_item.text()) if note_item else 0.0
            data["taches"].append({"name": task_name, "note": note})
    
        # Extraire les informations des étudiants
        for row in range(1, self.table.rowCount()):
            etudiant_data = {}
            etudiant_data["name"] = self.table.item(row, 0).text()
    
            # Extraire les notes
            notes = []
            barem_coms = ""
            for col in range(1, self.table.columnCount() - 2):
                widget: ComboBoxWidget = self.table.cellWidget(row, col)
                if not widget:
                    continue
                selected_note = widget.current_text if widget else ""
                
                barem_txt = list(self._barem["name"].keys())[widget.value]
                barem_com = list(self._barem["name"].values())[widget.value]
                barem_coms += f"- {barem_txt} | {self.table.horizontalHeaderItem(col).text()} | {barem_com}\n"

                notes.append(selected_note)
            etudiant_data["notes"] = notes

            # Extraire le total
            note_item = self.table.item(row, self.table.columnCount() - 2)
            etudiant_data["total"] = note_item.text() if note_item else ""

            # Extraire les commentaires
            commentaire_item = self.table.item(row, self.table.columnCount() - 1)
            etudiant_data["baremComentaires"] = barem_coms
            etudiant_data["commentaires"] = commentaire_item.text() if commentaire_item else ""
    
            data["etudiants"].append(etudiant_data)
    
        # Sauvegarder les données dans le fichier JSON
        with open(self._file, 'w', encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4, cls=JsonEncoder)