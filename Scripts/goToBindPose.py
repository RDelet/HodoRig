# coding=ascii

"""
!@Brief Go to bind pose.

File Path: {s_path}
"""

import traceback

from ..Core.logger import log
from ..Nodes.node import Node


kMayaMenu = True
kCategory = "Joint"
kAnnotation = "Go To BindPose"
kImage = None
kScriptName = 'Go To BindPose'


def main():
    try:
        selected = Node.selected(node_type="joint")
        if not selected:
            raise RuntimeError("No joint selected !")

        for jnt in selected:
            jnt.go_to_bindpose()
    except Exception:
        log.error(traceback.format_exc())
