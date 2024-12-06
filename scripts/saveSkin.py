# coding=ascii

"""
!@Brief Save selected skin cluster.
    - Select all mesh you want to save
    - Select directory to save files

File Path: {s_path}
"""

import logging
import os
import traceback

try:
    from PySide2 import QtWidgets
except:
    from PySide6 import QtWidgets

from maya import cmds

from ..Core import constants
from ..Core.logger import log
from ..Helpers.skin import Skin
from ..Ui import utils

log = logging.getLogger('Save Skin')
log.setLevel(logging.INFO)

kMayaMenu = True

kCategory = "Skin"
kAnnotation = "Save skin on selected mesh"
kImage = None
kScriptName = 'Save Skin'


def _save_skin(node: str, directory: str):
    try:
        skin = Skin.get(node)
        if not skin:
            log.debug(f"Node {node} does not have skin.")
            return
        short_name = node.split("|")[-1].split(":")[-1]
        file_name = f"{short_name}.{constants.kSkinExtension}"
        file_path = os.path.normpath(os.path.join(directory, file_name))
        skin.save(file_path)
    except Exception:
        log.error(f"Error on save skin of {node} !")
        log.error(traceback.format_exc())


def process(*args, **kwargs):
    title = "Select Skin Folder"
    directory = QtWidgets.QFileDialog.getExistingDirectory(utils.main_window(), title)
    if not directory:
        return

    selected = cmds.ls(selection=True, long=True) or []
    for node in selected:
        _save_skin(node, directory)


def main():
    try:
        process()
    except Exception:
        log.error(traceback.format_exc())
