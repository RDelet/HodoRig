from __future__ import annotations
import math
from typing import Optional

from maya import cmds
from maya.api import OpenMaya

from ..Core import _factory
from .dagNode import DAGNode


to_rad = math.radians
to_deg = math.degrees


@_factory.register()
class Transform(DAGNode):

    kApiType = OpenMaya.MFn.kTransform

    def duplicate(self, name: Optional[str] = None, parent: Optional[str | Transform] = None) -> Transform:
        new_node = super().duplicate(name=name, parent=parent)
        new_node.snap(self)

        return new_node

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
        if isinstance(value, (OpenMaya.MPoint, OpenMaya.MVector)):
            value = [value.x, value.y, value.z]
        cmds.xform(self.name, translation=value, objectSpace=not world, worldSpace=world)
    
    def rotation(self, world: bool = True) -> OpenMaya.MEulerRotation:
        rot = cmds.xform(self.name, query=True,
                         rotation=True, objectSpace=not world, worldSpace=world)
        return OpenMaya.MEulerRotation(to_rad(rot[0]), to_rad(rot[1]), to_rad(rot[2]))

    def set_rotation(self, value: list | OpenMaya.MVector | OpenMaya.MEulerRotation,
                     world: bool = True):
        if isinstance(value, OpenMaya.MEulerRotation):
            value = [math.degrees(x) for x in value]
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
    
    @property
    def shapes(self) -> list:
        shapes = []
        for i in range(self._mfn.childCount()):
            child = self._mfn.child(i)
            if child.hasFn(OpenMaya.MFn.kShape):
                shapes.append(self.get(child))

        return shapes

    def snap(self, node: str | OpenMaya.MObject | Transform, world: bool = True):
        if isinstance(node, (str, OpenMaya.MObject)):
            node = self(node)
        if not isinstance(node, Transform):
            raise RuntimeError(f"Node must be a transform not {type(node)}")
        self.set_matrix(node.matrix(world=world), world=world)
