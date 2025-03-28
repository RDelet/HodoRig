"""!@Brief Blend builder.
           Select joints and launch this code

from HodoRig.Core import constants as cst
from HodoRig.Rig.module import Module
from HodoRig.Rig.fkBuilder import FKBuilder
from HodoRig.Rig.ikBuilder import IKBuilder
from HodoRig.Rig.blendBuilder import BlendBuilder
from HodoRig.Nodes.node import Node


# ------------------------------------------
# Without Module
# ------------------------------------------

# Create Ik
ik_builder = IKBuilder()

# Create Fk
fk_builder = FKBuilder()
fk_builder._settings.set("shapeScale", 1.0)

# Create blender
sources = Node.selected(node_type="joint")
blend_builder = BlendBuilder("L_0_Hodor", sources)
blend_builder._settings.set(cst.kBlendName, "ikFkBlend")
blend_builder.add_children(ik_builder)
blend_builder.add_children(fk_builder)
blend_builder.build()

# ------------------------------------------
# With Module
# ------------------------------------------

# Create Module
sources = Node.selected(node_type="joint")
module = Module("L_0_Hodor", sources)

# Create blender
blend_builder = BlendBuilder()
blend_builder._settings.set(cst.kBlendName, "ikFkBlend")
module.add_builder(blend_builder)

# Create Ik
ik_builder = IKBuilder()
blend_builder.add_children(ik_builder)

# Create Fk
fk_builder = FKBuilder()
fk_builder._settings.set(cst.kShapeScale, 1.0)
blend_builder.add_children(fk_builder)

# Build Module
module.build()
"""

from __future__ import annotations
from typing import Optional, List

from maya import cmds

from ..Core import constants as cst
from ..Core.nameBuilder import NameBuilder
from ..Core.settings import Setting
from ..Nodes.node import Node
from ..Builders.builderState import BuilderState
from .rigBuilder import RigBuilder


class BlendBuilder(RigBuilder):

    def __init__(self, name: Optional[str | NameBuilder] = NameBuilder(),
                 sources: Optional[List[Node]]= []):
        super().__init__(name, sources)

        self._build_rig_group = False

        self._manipulator = None
        self._reverse_blend = None
        self._blend_name = None
        self._hook_a = None
        self._hook_b = None
        self._manipulator_a = None
        self._manipulator_b = None
    
    def _init_settings(self):
        self._settings.add(Setting(cst.kBlendName, "blender"))

    def _get_settings(self):
        self._blend_name = self._settings.value(cst.kBlendName)
    
    def _build(self, *args, **kwargs):
        super()._build(*args, **kwargs)
        self._build_children(*args, **kwargs)
        self._build_attribute()
        self._build_reverse_blend()
        self._build_constraint()
        self._connect_manipulators()

    def _build_children(self, *args, **kwargs):
        for builder in self._children:
            builder.build(*args, **kwargs)
            if not builder.state.value == BuilderState.kBuilt:
                raise RuntimeError(f"Error on build {builder.name} !")
        
        self._hook_a = self._children[0]._output_blend
        self._hook_b = self._children[1]._output_blend
        self._manipulator_a = self._children[0]._manipulators
        self._manipulator_b = self._children[1]._manipulators
        if len(self._hook_a) != len(self._hook_b):
            raise RuntimeError(f"Mismatch output node between {self._children[0].name} and {self._sub_builders[1].name}")

    def _build_attribute(self):
        manipulators = self._manipulator_a + self._manipulator_b
        self._manipulator = manipulators[0]
        self._manipulator.add_settings_attribute("blenderSettings")
        self._manipulator.add_attribute(self._blend_name, cst.kFloat, keyable=True, min=0.0, max=1.0)
        proxy_attr = f"{manipulators[0]}.{self._blend_name}"
        for manipulator in manipulators[1:]:
            manipulator.add_settings_attribute("blenderSettings")
            manipulator.add_attribute(self._blend_name, cst.kFloat,
                                            keyable=True, min=0.0, max=1.0, proxy=proxy_attr)
    
    def _build_reverse_blend(self):
        self._reverse_blend = Node.create("floatMath")
        self._manipulator.connect_to(self._blend_name, f"{self._reverse_blend}.floatB")
        self._reverse_blend.set_attribute("operation", 1)
    
    def _build_constraint(self):
        for hook_a, hook_b, src in zip(self._hook_a, self._hook_b, self._sources):
            cst = Node.get(cmds.parentConstraint(hook_a, hook_b, src, maintainOffset=True)[0])
            cst_attrs = cmds.parentConstraint(cst, query=True, weightAliasList=True)
            cst.set_attribute("interpType", 2)
            self._manipulator.connect_to(self._blend_name, f"{cst}.{cst_attrs[0]}")
            self._reverse_blend.connect_to("outFloat", f"{cst}.{cst_attrs[1]}")

    def _connect_manipulators(self):
        for manipulator in self._manipulator_a:
            self._manipulator.connect_to(self._blend_name, f"{manipulator}.visibility")
        for manipulator in self._manipulator_b:
            self._reverse_blend.connect_to("outFloat", f"{manipulator}.visibility")
    
    def add_children(self, builder: RigBuilder):
        if len(self._children) == 2:
            raise RuntimeError("You already have to builder set !")
        super().add_children(builder)
        builder._is_blended = True
