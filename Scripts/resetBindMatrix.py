# coding=ascii

"""
!@Brief Reset bind matrix from selected joint.

File Path: {s_path}
"""

import traceback

from ..Core.logger import log
from ..Nodes.node import Node


kMayaMenu = True
kCategory = "Joint"
kAnnotation = "Reset BindMatrix from selected joint"
kImage = None
kScriptName = 'Reset BindMatrix'


def main():
    try:
        selected = Node.selected(node_type="joint")
        if not selected:
            raise RuntimeError("No joint selected !")

        for jnt in selected:
            jnt.reste_bind_matrix()
    except Exception:
        log.error(traceback.format_exc())
