"""!@Brief IK builder.
           Select joints and launch this code

from HodoRig.Rig.module import Module
from HodoRig.Rig.ikBuilder import IKBuilder
from HodoRig.Nodes.node import Node

# ------------------------------------------
# Without Module
# ------------------------------------------

sources = Node.selected(node_type="joint")
ik_builder = IKBuilder("L_0_Hodor", sources)
ik_builder.build()

# ------------------------------------------
# With Module
# ------------------------------------------

# Create Module
sources = Node.selected(node_type="joint")
module = Module("L_0_Hodor", sources)

# Create Ik
ik_builder = IKBuilder()
module.add_builder(ik_builder)

# Build Module
module.build()
"""

from __future__ import annotations
from typing import Optional, List

from maya import cmds
from maya.api import OpenMaya

from ..Core import constants as cst
from ..Core.nameBuilder import NameBuilder
from ..Core.settings import Setting
from ..Helpers import utils
from ..Helpers.color import Color
from .rigBuilder import RigBuilder
from ..Nodes.node import Node
from ..Nodes.transform import Transform
from .manipulatorBuilder import ManipulatorBuilder


class IKBuilder(RigBuilder):

    def __init__(self, name: Optional[str | NameBuilder] = NameBuilder(),
                 sources: Optional[List[Node]]= []):
        super().__init__(name, sources)

        self._ikh = None
        self._eff = None

        self.__solver = None
        self.__snap_rotation = None
        self.__pv_distance = None
        self.__shape_scale = None
    
    def _init_settings(self):
        self._settings.add(Setting(cst.kSolver, cst.kIkRPsolver))
        self._settings.add(Setting(cst.kSnapRotation, True))
        self._settings.add(Setting(cst.kPvDistance, 20))
        self._settings.add(Setting(cst.kShapeScale, 10.0))

    def _get_settings(self):
        self.__solver = self._settings.value(cst.kSolver)
        self.__snap_rotation = self._settings.value(cst.kSnapRotation)
        self.__pv_distance = self._settings.value(cst.kPvDistance)
        self.__shape_scale = self._settings.value(cst.kShapeScale)

    def _check_validity(self):
        super()._check_validity()
        if len(self._sources) < 2:
            raise RuntimeError("IK builder need to have 2 sources minimum !")

    def _build(self, *args, **kwargs):
        super()._build(*args, **kwargs)

        self._duplicate_sources()
        self._create_handle()
        self._build_manipulator()
        self._constrain_sources()

    def _build_manipulator(self):
        self._build_effecteur(self.__shape_scale)
        self._build_pole_vector(self.__shape_scale)

    def _build_effecteur(self, shape_scale: float):
        builder_eff = ManipulatorBuilder(f"{self._sources[-1]}Ik")
        color = Color.from_name(self._name)
        builder_eff.build(self._parent_grp, shape="rounded_square", shape_dir=0, scale=shape_scale, color=color)
        if self.__snap_rotation:
            builder_eff.reset.snap(self._sources[-1])
        else:
            builder_eff.reset.set_position(self._sources[-1].position())
        
        eff_manipulator = builder_eff.node
        self._ikh.parent = eff_manipulator
        cmds.orientConstraint(eff_manipulator, self._output_blend[-1], maintainOffset=True)
        self._manipulators.append(eff_manipulator) 
    
    def _build_pole_vector(self, shape_scale: float):
        builder_pv = ManipulatorBuilder(f"{self._sources[-1]}Pv")
        color = Color.from_name(self._name)
        builder_pv.build(self._parent_grp, shape="ball", shape_dir=0, scale=shape_scale, color=color)
        builder_pv.reset.set_position(self._compute_aim())

        pv_manipulator = builder_pv.node
        cmds.poleVectorConstraint(pv_manipulator, self._ikh)
        self._manipulators.append(pv_manipulator)

    def _duplicate_sources(self):
        parent = self._parent_grp
        for i, src in enumerate(self._sources):
            name = NameBuilder.from_name(src.short_name)
            name.type = "IK"
            new_node = src.duplicate(name=name, parent=parent)
            new_node.freeze_rotation()
            if i == 0:
                new_node.set_attribute(cst.kVisibility, False)
                parent_jnt = src.parent
                if parent_jnt:
                    cmds.parentConstraint(parent_jnt, new_node, maintainOffset=True)
            self._output_blend.append(new_node)
            parent = new_node

    def _create_handle(self):
        ikh, eff = cmds.ikHandle(startJoint=self._output_blend[0], endEffector=self._output_blend[-1], solver=self.__solver)
        self._eff = Transform.get(eff)
        self._ikh = Transform.get(ikh)
        self._ikh.set_attribute(cst.kVisibility, False)
    
    def _compute_aim(self) -> OpenMaya.MVector:
        root_pos, mid_pos, effector_pos = [node.position() for node in self._sources]
        a = mid_pos - root_pos
        b = (effector_pos - root_pos).normal()
        dot = abs(a.normal() * b)
        if dot == 1.0:
            raise RuntimeError("Vectors or collinear !")

        projected_mid = root_pos + b.normal() * (a.length() * dot)
        pv_dir = (mid_pos - projected_mid).normal()

        return OpenMaya.MVector(mid_pos + pv_dir * self.__pv_distance)

    def _constrain_sources(self):
        if self._is_blended:
            return

        for src, dst in zip(self._output_blend, self._sources):
            cmds.parentConstraint(src, dst, maintainOffset=True)
