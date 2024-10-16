# coding=ascii

"""
!@Brief Reset bind matrix from selected joint.

File Path: {s_path}
"""

import traceback

from maya import cmds

from ..Core.logger import log
from ..Helpers import joint


kMayaMenu = True
kCategory = "Joint"
kAnnotation = "Reset BindMatrix from selected joint"
kImage = None
kScriptName = 'Reset BindMatrix'


def main():
    try:
        selection = cmds.ls(selection=True, long=True, type="joint")
        if not selection:
            raise RuntimeError("No joint selected !")

        for jnt in selection:
            joint.reste_bind_matrix(jnt)
    except Exception:
        log.error(traceback.format_exc())
