from __future__ import annotations
import math
from typing import Optional

from maya import cmds
from maya.api import OpenMaya

from ..Core import _factory
from ..Helpers import utils
from ..Nodes._transformNode import _TransformNode


@_factory.register()
class _Joint(_TransformNode):

    kApiType = OpenMaya.MFn.kJoint

    def bind_pose(self) -> Optional[OpenMaya.MMatrix]:
        bp = cmds.getAttr(f"{self.name}.bindPose")
        return OpenMaya.MMatrix(bp) if bp else None
    
    def set_bind_pose(self, matrix: OpenMaya.MMatrix):
        cmds.setAttr(f"{self.name}.bindPose", matrix, type='matrix')

    def joint_orient(self) -> list :
        return cmds.getAttr(f"{self.name}.jointOrient")[0]

    def set_joint_orient(self, value: list | tuple | OpenMaya.MVector | OpenMaya.MEulerRotation):
        if isinstance(value, OpenMaya.MEulerRotation):
            value = [math.degrees(x) for x in value]
        is_lock = cmds.getAttr(f"{self.name}.jointOrient", lock=True)
        cmds.setAttr(f"{self.name}.jointOrient", lock=False)
        cmds.setAttr(f"{self.name}.jointOrient", *value, lock=is_lock)
    
    def preferred_angle(self) -> list :
        return cmds.getAttr(f"{self.name}.preferredAngle")[0]

    def set_preferred_angle(self, value: list | tuple | OpenMaya.MVector | OpenMaya.MEulerRotation):
        if isinstance(value, OpenMaya.MEulerRotation):
            value = [math.degrees(x) for x in value]
        is_lock = cmds.getAttr(f"{self.name}.preferredAngle", lock=True)
        cmds.setAttr(f"{self.name}.preferredAngle", lock=False)
        cmds.setAttr(f"{self.name}.preferredAngle", *value, lock=is_lock)

    def freeze_rotation(self, to_rotate: bool = True, recursive: bool = False):
        world_matrix = self.matrix()
        self.set_rotation([0.0, 0.0, 0.0], world=False)
        self.set_joint_orient([0.0, 0.0, 0.0])
        self.set_matrix(world_matrix)
        rotation = self.rotation(world=False)
        self.set_preferred_angle(rotation)
        if to_rotate:
            self.set_rotation(rotation, world=False)
        else:
            self.set_rotation([0.0, 0.0, 0.0], world=False)
            self.set_joint_orient(rotation)
        
        if recursive:
            for child in self.children(type="joint"):
                child.freeze_rotation(to_rotate=to_rotate, recursive=recursive)
    
    def reste_bind_matrix(self, recursive: bool = True):

        matrix = self.matrix()
        self.set_bind_pose(matrix)

        destinations = cmds.listConnections(f"{self.name}.worldMatrix[0]", source=False, destination=True,
                                            type="skinCluster", plugs=True) or []
        for dst in destinations:
            skin_node, attr = dst.split(".")
            matrix_id = (attr.split("[")[-1].split("]")[0])
            cmds.setAttr(f"{skin_node}.bindPreMatrix[{matrix_id}]", matrix.inverse(), type="matrix")

        if recursive:
            for child in self.children(type="joint"):
                child.reste_bind_matrix(recursive=recursive)


    def go_to_bindpose(self, recursive: bool = True):
        bindpose = self.bind_pose()
        if bindpose:
            cmds.xform(self.name, matrix=bindpose, worldSpace=True)

        if recursive:
            for child in self.children(type="joint"):
                child.go_to_bindpose(recursive=recursive)
