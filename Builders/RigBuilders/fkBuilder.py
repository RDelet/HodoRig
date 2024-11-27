"""!@Brief FK builder.
           Select joints and launch this code

from HodoRig.Builders.RigBuilders.fkBuilder import FKBuilder
from HodoRig.Nodes.node import Node


sources = Node.selected(node_type="joint")
fk_builder = FKBuilder("L_0_Groot", sources)
fk_builder._settings.set("shapeScale", 1.0)
fk_builder.build()
"""

from __future__ import annotations
from typing import List

from maya import cmds
from maya.api import OpenMaya

from ...Core.nameBuilder import NameBuilder
from ...Core.settings import Setting
from ...Helpers import utils
from ...Helpers.color import Color
from ..RigBuilders.rigBuilder import RigBuilder
from .manipulatorBuilder import ManipulatorBuilder


class FKBuilder(RigBuilder):

    _kShapeDir = "shapeDir"
    _kShapeScale = "shapeScale"

    def __init__(self, name: str | NameBuilder, sources: List[str], is_blended: bool = False):
        super().__init__(name, sources, is_blended=is_blended)

        self.__shape_dir = None
        self.__shape_scale = None

    def _init_settings(self):
        self._settings.add(Setting(self._kShapeDir, 0))
        self._settings.add(Setting(self._kShapeScale, 10.0))

    def _get_settings(self):
        self.__shape_dir = self._settings.value(self._kShapeDir)
        self.__shape_scale = self._settings.value(self._kShapeScale)

    def _build(self, parent: OpenMaya.MObject = utils._nullObj):
        super()._build()
        
        parent = self._rig_group
        for i, jnt in enumerate(self._sources):
            builder = ManipulatorBuilder(jnt.short_name)
            color = Color.from_name(jnt.short_name)
            builder.build(parent, shape="circle",
                          shape_dir=self.__shape_dir,
                          scale=self.__shape_scale, color=color)
            builder.reset.snap(jnt)
            parent = builder.node
            self._manipulators.append(builder.node)
            self._output_blend.append(builder.node)

            if i == 0:
                parent_jnt = jnt.parent
                if parent_jnt:
                    cmds.parentConstraint(parent_jnt, builder.reset, maintainOffset=True)

            if not self._is_blended:
                cmds.parentConstraint(builder.node, jnt)
