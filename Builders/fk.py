from __future__ import annotations

from maya import cmds
from maya.api import OpenMaya

from ..Helpers import utils
from ..Builders.rigBuilder import RigBuilder
from .manipulator import Manipulator


# ToDo: Create factory
class FK(RigBuilder):

    def _build(self, parent: OpenMaya.MObject = utils._nullObj,
               shape: str = "circle", shape_dir: int = 0, scale: float = 1.0):
        super()._build()
        
        parent = utils._nullObj
        for jnt in self._sources:
            builder = Manipulator(jnt.split("|")[-1].split(":")[-1])
            builder.build(parent, shape=shape, shape_dir=shape_dir, scale=scale)
            builder.reset.snap(jnt)
            parent = builder.node.object
            self._manipulators.append(builder.node)

            if not self._is_blended:
                cmds.parentConstraint(builder.node.name, jnt)
