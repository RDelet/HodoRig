# coding=ascii

"""
!@Brief Go to bind pose.

File Path: {s_path}
"""

import traceback

from maya import cmds

from ..Core.logger import log
from ..Helpers import joint


kMayaMenu = True
kCategory = "Joint"
kAnnotation = "Go To BindPose"
kImage = None
kScriptName = 'Go To BindPose'


def main():
    try:
        selection = cmds.ls(selection=True, long=True, type="joint")
        if not selection:
            raise RuntimeError("No joint selected !")

        for jnt in selection:
            joint.go_to_bindpose(jnt)
    except Exception:
        log.error(traceback.format_exc())
