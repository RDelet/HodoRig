from __future__ import annotations
import math

from maya import cmds
from maya.api import OpenMaya

from HodoRig.Core import _factory
from HodoRig.Nodes._dagNode import _DAGNode
from HodoRig.Nodes.node import Node


to_rad = math.radians
to_deg = math.degrees


@_factory.register()
class _TransformNode(_DAGNode):

    kApiType = OpenMaya.MFn.kTransform

    def matrix(self, world: bool = True) -> OpenMaya.MMatrix:
        matrix = cmds.xform(self.name, query=True,
                            matrix=True, objectSpace=not world, worldSpace=world)
        return OpenMaya.MMatrix(matrix)
    
    def set_matrix(self, value: list | OpenMaya.MMatrix, world: bool = True):
        cmds.xform(self.name, matrix=value, objectSpace=not world, worldSpace=world)

    def position(self, world: bool = True) -> OpenMaya.MPoint:
        pos = cmds.xform(self.name, query=True,
                         translation=True, objectSpace=not world, worldSpace=world)
        return OpenMaya.MPoint(pos)

    def set_position(self, value: list | OpenMaya.MPoint | OpenMaya.MVector, world: bool = True):
        cmds.xform(self.name, translation=value, objectSpace=not world, worldSpace=world)
    
    def rotation(self, world: bool = True) -> OpenMaya.MEulerRotation:
        rot = cmds.xform(self.name, query=True,
                         rotation=True, objectSpace=not world, worldSpace=world)
        return OpenMaya.MEulerRotation(to_rad(rot[0]), to_rad(rot[1]), to_rad(rot[2]))

    def set_rotation(self, value: list | OpenMaya.MVector | OpenMaya.MEulerRotation,
                     world: bool = True):
        cmds.xform(self.name, rotation=value, objectSpace=not world, worldSpace=world)
    
    def quaternion(self, world: bool = True) -> OpenMaya.MQuaternion:
        return self.rotation(world=world).asQuaternion()
    
    def set_quaternion(self, value: OpenMaya.MEulerRotation | OpenMaya.MQuaternion,
                       world: bool = True):
        if isinstance(value, OpenMaya.MQuaternion):
            value = value.asEulerRotation()
        self.set_rotation(value, world=world)
    
    def scale(self, world: bool = True) -> OpenMaya.MVector:
        scale = cmds.xform(self.name, query=True,
                           scale=True, objectSpace=not world, worldSpace=world)
        return OpenMaya.MVector(scale[0], scale[1], scale[2])

    def set_scale(self, value: list | OpenMaya.MVector, world: bool = True):
        cmds.xform(self.name, scale=value, objectSpace=not world, worldSpace=world)

    def snap(self, node: str | OpenMaya.MObject | _TransformNode, world: bool = True):
        if isinstance(node, (str, OpenMaya.MObject)):
            node = Node(node)
        if not isinstance(node, _TransformNode):
            raise RuntimeError(f"Node must be a transform not {type(node)}")
        
        if world:
            self.world_matrix = node.world_matrix
        else:
            self.matrix = node.matrix
