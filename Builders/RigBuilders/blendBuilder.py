"""!@Brief FK builder.
           Select joints and launch this code

from HodoRig.Builders.RigBuilders.fkBuilder import FKBuilder
from HodoRig.Builders.RigBuilders.ikBuilder import IKBuilder
from HodoRig.Builders.RigBuilders.blendBuilder import BlendBuilder
from HodoRig.Nodes.node import Node

sources = Node.selected(node_type="joint")

# Ik
ik_builder = IKBuilder(name="Hodor", sources=sources)
# Fk
fk_builder = FKBuilder("L_0_Groot", sources)
fk_builder._settings.set("shapeScale", 1.0)
# Blend
blend_builder = BlendBuilder("L_0_Groot_BLENDER", sources)
blend_builder.add_sub_builder(ik_builder)
blend_builder.add_sub_builder(fk_builder)
blend_builder._settings.set("blendAttrName", "ikFkBlend")
blend_builder.build()
"""

from __future__ import annotations
from typing import List

from maya import cmds

from ...Core.nameBuilder import NameBuilder
from ...Core.settings import Setting
from ...Helpers import utils
from ...Helpers.color import Color
from ...Nodes.node import Node
from ..builderState import BuilderState
from ..RigBuilders.rigBuilder import RigBuilder
from .manipulatorBuilder import ManipulatorBuilder


class BlendBuilder(RigBuilder):

    def __init__(self,  name: str | NameBuilder, sources: List[RigBuilder]):
        super().__init__(name, sources)

    def _init_settings(self):
        self._settings.add(Setting("blendAttrName", "blender"))

        self._manipulator = None
        self._reverse_blend = None

    def _build_manipulators(self):
        manip_name = self._name.clone()
        manip_name.type = "Settings"
        builder_pv = ManipulatorBuilder(manip_name)
        color = Color.from_name(manip_name)
        builder_pv.build(utils._nullObj, shape="cross", shape_dir=2, color=color)
        self._manipulator = builder_pv.node
        self._manipulator.snap(self._sources[0])
        self._manipulators.append(self._manipulator)

        blend_name = self._settings.value("blendAttrName")
        cmds.addAttr(self._manipulator.name, longName=blend_name, attributeType="float",
                     keyable=True, min=0.0, max=1.0)
    
    def _build_reverse_blend(self):
        # ToDo: Load plugin on HodoRig init
        self._reverse_blend = Node.create("floatMath")
        blend_name = self._settings.value("blendAttrName")
        cmds.connectAttr(f"{self._manipulator.name}.{blend_name}",
                         f"{self._reverse_blend.name}.floatB")
        cmds.setAttr(f"{self._reverse_blend.name}.operation", 1)

    def _build(self):
        super()._build()
        blend_name = self._settings.value("blendAttrName")

        for builder in self._sub_builders:
            builder.build()
        
        src_a = self._sub_builders[0]._output_blend
        src_b = self._sub_builders[1]._output_blend
        if len(src_a) != len(src_b):
            raise RuntimeError(f"Mismatch output node between {self._sub_builders[0].name} and {self._sub_builders[1].name}")
         
        self._build_manipulators()
        self._build_reverse_blend()

        for manipulator in self._sub_builders[0]._manipulators:
            cmds.connectAttr(f"{self._manipulator.name}.{blend_name}", f"{manipulator.name}.visibility")
        
        for manipulator in self._sub_builders[1]._manipulators:
            cmds.connectAttr(f"{self._reverse_blend.name}.outFloat", f"{manipulator.name}.visibility")

        for node_a, node_b, src in zip(src_a, src_b, self._sources):
            # ToDo: check attributes
            cst = cmds.parentConstraint(node_a.name, node_b.name, src.name, maintainOffset=True)[0]
            cst_attrs = cmds.parentConstraint(cst, query=True, weightAliasList=True)
            cmds.setAttr(f"{cst}.interpType", 2)
            cmds.connectAttr(f"{self._manipulator.name}.{blend_name}", f"{cst}.{cst_attrs[0]}")
            cmds.connectAttr(f"{self._reverse_blend.name}.outFloat", f"{cst}.{cst_attrs[1]}")
     
    def add_sub_builder(self, builder: RigBuilder):
        if len(self._sub_builders) == 2:
            raise RuntimeError("You already have to builder set !")
        if builder in self._sub_builders:
            raise RuntimeError(f"Builder {builder.name} already set !")
        if builder.state.value == BuilderState.kBuilt:
            raise RuntimeError(f"Builder {builder.name} already built !")

        builder._is_blended = True
        builder._sources = self._sources

        self._sub_builders.append(builder)
