"""!@Brief IK builder.
           Select joints and launch this code

from HodoRig.Builders.RigBuilders.ikBuilder import IKBuilder
from HodoRig.Nodes.node import Node

sources = Node.selected(node_type="joint")
ik_builder = IKBuilder(name="Hodor", sources=sources)
ik_builder.build()
"""

from __future__ import annotations
from typing import Optional, List

from maya import cmds
from maya.api import OpenMaya

from ...Helpers.color import Color
from ...Core.nameBuilder import NameBuilder
from ...Core.settings import Setting
from ...Helpers import utils
from ..RigBuilders.rigBuilder import RigBuilder
from ...Nodes.transform import Transform
from .manipulatorBuilder import ManipulatorBuilder


class IKBuilder(RigBuilder):

    def __init__(self,  name: str | NameBuilder, sources: List[str], is_blended: bool = False):
        super().__init__(name=name, sources=sources, is_blended=is_blended)

        self._ikh = None
        self._eff = None
    
    def _init_settings(self):
        self._settings.add(Setting("solver", "ikRPsolver"))
        self._settings.add(Setting("snapRotation", True))
        self._settings.add(Setting("pvDistance", 20))
        self._settings.add(Setting("shapeScale", 10.0))

    def _check_validity(self):
        super()._check_validity()
        if len(self._sources) < 2:
            raise RuntimeError("IK builder need to have 2 sources minimum !")

    def _build(self, parent: OpenMaya.MObject = utils._nullObj):
        super()._build(parent=parent)
        
        self._duplicate_sources()
        self._create_handle()
        self._build_manipulator()
        self._constrain_sources()

    def _build_manipulator(self):
        scale_factor = self._settings.value("shapeScale")

        self._build_effecteur(scale_factor)
        self._build_pole_vector(scale_factor)

    def _build_effecteur(self, shape_scale: float):
        builder_eff = ManipulatorBuilder(f"IK_{self._name}")
        color = Color.from_name(self._name)
        builder_eff.build(utils._nullObj, shape="rounded_square", shape_dir=0, scale=shape_scale, color=color)
        eff_manipulator = builder_eff.node
        if self._settings.value("snapRotation"):
            eff_manipulator.snap(self._sources[-1])
        else:
            eff_manipulator.set_position(self._sources[-1].position)
        
        self._ikh.parent = eff_manipulator
        cmds.orientConstraint(eff_manipulator.name, self._output_blend[-1].name, maintainOffset=True)
        self._manipulators.append(eff_manipulator) 
    
    def _build_pole_vector(self, shape_scale: float):
        builder_pv = ManipulatorBuilder(f"PV_{self._name}")
        color = Color.from_name(self._name)
        builder_pv.build(utils._nullObj, shape="ball", shape_dir=0, scale=shape_scale, color=color)
        pv_manipulator = builder_pv.node
        pv_manipulator.set_position(self._compute_aim())

        cmds.poleVectorConstraint(pv_manipulator.name, self._ikh.name)
        self._manipulators.append(pv_manipulator)

    def _duplicate_sources(self, parent: Optional[str | Transform] = None):
        parent = None
        for src in self._sources:
            name = NameBuilder.from_name(src.short_name)
            name.type = "IK"
            new_node = src.duplicate(name=name, parent=parent)
            new_node.freeze_rotation()
            self._output_blend.append(new_node)
            parent = new_node

    def _create_handle(self):
        ikh, eff = cmds.ikHandle(startJoint=self._output_blend[0].name,
                                 endEffector=self._output_blend[-1].name,
                                 solver=self._settings.value("solver"))
    
        self._ikh = Transform.get(ikh)
        self._eff = Transform.get(eff)
    
    def _compute_aim(self) -> OpenMaya.MVector:
        root_pos, mid_pos, effector_pos = [node.position() for node in self._sources]
        a = mid_pos - root_pos
        b = (effector_pos - root_pos).normal()
        dot = abs(a.normal() * b)
        if dot == 1.0:
            raise RuntimeError("Vectors or collinear !")

        projected_mid = root_pos + b.normal() * (a.length() * dot)
        pv_dir = (mid_pos - projected_mid).normal()

        return OpenMaya.MVector(mid_pos + pv_dir * self._settings.value("pvDistance"))

    def _constrain_sources(self):
        if self._is_blended:
            return

        for src, dst in zip(self._output_blend, self._sources):
            cmds.parentConstraint(src.name, dst.name, maintainOffset=True)
