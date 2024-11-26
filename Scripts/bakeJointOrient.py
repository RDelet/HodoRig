# coding=ascii

"""
!@Brief Bake joint rotation to jointOrient attribute.

File Path: {s_path}
"""

import traceback

from ..Core.logger import log
from ..Nodes.node import Node


kMayaMenu = True
kCategory = "Joint"
kAnnotation = "Bake joint rotation to jointOrient attribute"
kImage = None
kScriptName = 'BakeJointOrient'


def main():
    try:
        selected = Node.selected(node_type="joint")
        if not selected:
            raise RuntimeError("No joint selected !")

        for jnt in selected:
            jnt.freeze_rotation(to_rotate=False, recursive=False)
    except Exception:
        log.error(traceback.format_exc())
