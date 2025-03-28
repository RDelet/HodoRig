"""!@Brief FK builder.
           Select joints and launch this code

from HodoRig.Core import constants as cst
from HodoRig.Rig.module import Module
from HodoRig.Rig.fkBuilder import FKBuilder
from HodoRig.Nodes.node import Node


# ------------------------------------------
# Without Module
# ------------------------------------------

sources = Node.selected(node_type="joint")
fk_builder = FKBuilder("L_0_Hodor", sources)
fk_builder.build()

# ------------------------------------------
# With Module
# ------------------------------------------

# Create Module
sources = Node.selected(node_type="joint")
module = Module("L_0_Hodor", sources)
module._name

# Create Fk
fk_builder = FKBuilder()
fk_builder._settings.set(cst.kShapeScale, 300.0)
module.add_builder(fk_builder)

# Build Module
module.build()
"""

from __future__ import annotations
from typing import Optional, List

from maya import cmds

from ..Core import constants as cst
from ..Core.nameBuilder import NameBuilder
from ..Core.settings import Setting
from ..Helpers.color import Color
from ..Nodes.node import Node
from .rigBuilder import RigBuilder
from .manipulatorBuilder import ManipulatorBuilder


class FKBuilder(RigBuilder):

    def __init__(self, name: Optional[str | NameBuilder] = NameBuilder(),
                 sources: Optional[List[Node]]= []):
        super().__init__(name, sources)

        self.__shape_dir = None
        self.__shape_scale = None

    def _init_settings(self):
        self._settings.add(Setting(cst.kShapeDirection, 0))
        self._settings.add(Setting(cst.kShapeScale, 10.0))

    def _get_settings(self):
        self.__shape_dir = self._settings.value(cst.kShapeDirection)
        self.__shape_scale = self._settings.value(cst.kShapeScale)

    def _build(self, *args, **kwargs):
        super()._build(*args, **kwargs)

        parent = self._parent_grp
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
