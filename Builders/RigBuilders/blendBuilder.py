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

from ...Core import constants
from ...Core.nameBuilder import NameBuilder
from ...Core.settings import Setting
from ...Helpers import utils
from ...Helpers.color import Color
from ...Nodes.node import Node
from ..builderState import BuilderState
from ..RigBuilders.rigBuilder import RigBuilder
from .manipulatorBuilder import ManipulatorBuilder


class BlendBuilder(RigBuilder):

    _kBlendName = "blendName"

    def __init__(self,  name: str | NameBuilder, sources: List[RigBuilder]):
        super().__init__(name, sources)

        self._build_rig_group = False

        self.__manipulator = None
        self.__reverse_blend = None
        self.__blend_name = None
        self.__hook_a = None
        self.__hook_b = None
        self.__manipulator_a = None
        self.__manipulator_b = None
    
    def _init_settings(self):
        self._settings.add(Setting(self._kBlendName, "blender"))

    def _get_settings(self):
        self.__blend_name = self._settings.value(self._kBlendName)
    
    def _build(self):
        super()._build()
        self._build_sub_builders()
        self._build_attribute()
        self._build_reverse_blend()
        self._build_constraint()
        self._connect_manipulators()

    def _build_sub_builders(self):
        for builder in self._sub_builders:
            builder.build()
            if not builder.state.value == BuilderState.kBuilt:
                raise RuntimeError(f"Error on build {builder.name} !")
        
        self.__hook_a = self._sub_builders[0]._output_blend
        self.__hook_b = self._sub_builders[1]._output_blend
        self.__manipulator_a = self._sub_builders[0]._manipulators
        self.__manipulator_b = self._sub_builders[1]._manipulators
        if len(self.__hook_a) != len(self.__hook_b):
            raise RuntimeError(f"Mismatch output node between {self._sub_builders[0].name} and {self._sub_builders[1].name}")

    def _build_attribute(self):
        manipulators = self.__manipulator_a + self.__manipulator_b
        self.__manipulator = manipulators[0]
        self.__manipulator.add_settings_attribute("blenderSettings")
        self.__manipulator.add_attribute(self.__blend_name, constants.kFloat, keyable=True, min=0.0, max=1.0)
        proxy_attr = f"{manipulators[0]}.{self.__blend_name}"
        for manipulator in manipulators[1:]:
            manipulator.add_settings_attribute("blenderSettings")
            manipulator.add_attribute(self.__blend_name, constants.kFloat,
                                            keyable=True, min=0.0, max=1.0, proxy=proxy_attr)
    
    def _build_reverse_blend(self):
        self.__reverse_blend = Node.create("floatMath")
        self.__manipulator.connect_to(self.__blend_name, f"{self.__reverse_blend}.floatB")
        self.__reverse_blend.set_attribute("operation", 1)
    
    def _build_constraint(self):
        for hook_a, hook_b, src in zip(self.__hook_a, self.__hook_b, self._sources):
            cst = Node.get(cmds.parentConstraint(hook_a, hook_b, src, maintainOffset=True)[0])
            cst_attrs = cmds.parentConstraint(cst, query=True, weightAliasList=True)
            cst.set_attribute("interpType", 2)
            self.__manipulator.connect_to(self.__blend_name, f"{cst}.{cst_attrs[0]}")
            self.__reverse_blend.connect_to("outFloat", f"{cst}.{cst_attrs[1]}")

    def _connect_manipulators(self):
        for manipulator in self.__manipulator_a:
            self.__manipulator.connect_to(self.__blend_name, f"{manipulator}.visibility")
        for manipulator in self.__manipulator_b:
            self.__reverse_blend.connect_to("outFloat", f"{manipulator}.visibility")
     
    def add_sub_builder(self, builder: RigBuilder):
        if len(self._sub_builders) == 2:
            raise RuntimeError("You already have to builder set !")
        if builder in self._sub_builders:
            raise RuntimeError(f"Builder {builder} already set !")
        if builder.state.value == BuilderState.kBuilt:
            raise RuntimeError(f"Builder {builder} already built !")

        builder._is_blended = True
        builder._sources = self._sources

        self._sub_builders.append(builder)
