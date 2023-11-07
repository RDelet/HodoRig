# coding=ascii

"""
!@Brief QuickScripts template.

File Path: {s_path}

Add any help !
"""

import logging
import os
import traceback

from PySide2 import QtWidgets

from maya import cmds

from HodoRig.Core import constants
from HodoRig.Core.skin import Skin
from HodoRig.Ui import utils

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
        short_name = node.split("|")[-1].split(":")[-1]
        file_name = f"{short_name}.{constants.kSkinExtension}"
        file_path = os.path.normpath(os.path.join(directory, file_name))
        skin.save(file_path)
    except Exception:
        log.error(f"Error on save skin of {node} !")


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
