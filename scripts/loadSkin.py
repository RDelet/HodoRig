# coding=ascii

"""
!@Brief Load skin cluster from file.

File Path: {s_path}
"""

import logging
import traceback

try:
    from PySide2 import QtWidgets
except:
    from PySide6 import QtWidgets

from maya import cmds

from ..Helpers.skin import Skin
from ..Ui import utils

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

        skin_obj = Skin.find(skin.shape.object)
        if not skin_obj:
            skin.bind()
        else:
            skin.object = skin_obj
        skin.apply()
    except Exception:
        log.error(f"Error on load skin on {node} !")
        log.error(traceback.format_exc())


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
