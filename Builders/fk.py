"""!@Brief FK builder.
           Select joints and launch this code

from HodoRig.Builders.fk import FK
from HodoRig.Nodes.node import Node


sources = Node.selected(node_type="joint")
fk_builder = FK("L_0_Groot", sources)
fk_builder._settings.set("shapeScale", 1.0)
fk_builder.build()
"""

from __future__ import annotations

from maya import cmds
from maya.api import OpenMaya

from ..Core.settings import Setting
from ..Helpers import utils
from ..Helpers.color import Color
from ..Builders.rigBuilder import RigBuilder
from .manipulator import Manipulator


# ToDo: Create factory
class FK(RigBuilder):

    def _init_settings(self):
        self._settings.add(Setting("shapeName", "circle"))
        self._settings.add(Setting("shapeDir", 0))
        self._settings.add(Setting("shapeScale", 10.0))

    def _build(self, parent: OpenMaya.MObject = utils._nullObj):
        super()._build()

        print(self._name)

        shape_name = self._settings.value("shapeName")
        shape_dir = self._settings.value("shapeDir")
        shape_scale = self._settings.value("shapeScale")
        
        parent = utils._nullObj
        for jnt in self._sources:
            builder = Manipulator(jnt.short_name)
            color = Color.from_name(jnt.short_name)
            builder.build(parent, shape=shape_name, shape_dir=shape_dir, scale=shape_scale, color=color)
            builder.reset.snap(jnt)
            parent = builder.node
            self._manipulators.append(builder.node)

            if not self._is_blended:
                cmds.parentConstraint(builder.node.name, jnt.name)
