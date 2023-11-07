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

from HodoRig.Core.skin import Skin
from HodoRig.Ui import utils

log = logging.getLogger('Load Skin')
log.setLevel(logging.INFO)

kMayaMenu = True

kCategory = "Skin"
kAnnotation = "Load skin from file"
kImage = None
kScriptName = 'Load Skin'


def _load_skin(node: str, file_path: str):
    
    try:
        skin = Skin.read(file_path, shape_namespace=None, joint_namespace=None, joint_root=None)
        if not skin.shape:
            raise RuntimeError("No shape found !")

        skin_obj = Skin.find(skin.shape)
        if not skin_obj:
            skin.bind()
        skin.apply()
    except Exception:
        log.error(f"Error on save skin of {node} !")


def process(*args, **kwargs):
    title = "Select Skin File"
    file_path, _ = QtWidgets.QFileDialog.getOpenFileName(utils.main_window(), title)
    if not file_path:
        return

    selected = cmds.ls(selection=True, long=True) or []
    for node in selected:
        _load_skin(node, file_path)


def main():
    try:
        process()
    except Exception:
        log.error(traceback.format_exc())
