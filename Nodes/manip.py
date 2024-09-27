from __future__ import annotations
from typing import Optional

from maya import cmds
from maya.api import OpenMaya

from ..Helpers import utils

from ..Core import constants, _factory
from ..Core.nameBuilder import NameBuilder
from ..Builders.builder import Builder
from ..Nodes._transformNode import _TransformNode
from ..Nodes.node import Node
from ..Nodes._shape import _Shape


class ManipBuilder(Builder):

    def _build(self,name: str | NameBuilder, shape: str = "circle",
               shape_dir: int = None, scale: float = None, manip_type: str = constants.kFk) -> Manip:
        super()._build()

        if isinstance(name, str):
            name = NameBuilder.from_name(name)

        reset_obj = Node.create("transform", name=name.clone(type="RESET"))
        manip_obj = Node.create("transform", name.clone(type="MANIP"), parent=reset_obj.object)
        shapes = _Shape.load(shape, manip_obj.object, shape_dir=shape_dir, scale=scale)

        cmds.addAttr(manip_obj.name, longName=constants.kResetGroup, attributeType=constants.kMessage)
        cmds.connectAttr(f"{reset_obj.name}.{constants.kMessage}",
                         f"{manip_obj.name}.{constants.kResetGroup}", force=True)

        manip = Manip(manip_obj, type=manip_type, shapes=shapes)

        return manip


class Manip(_TransformNode):

    builder = ManipBuilder()

    def __init__(self, node: Optional[str | OpenMaya.MObject] = None,
                 type: Optional[str] = None, shapes: Optional[list | tuple] = None):
        super().__init__(node=node)

        self._reset = None
        self._shapes = shapes
        self._type = type
    
    @property
    def reset(self) -> _TransformNode:
        if not self._reset and self._object and utils.is_valid(self._object):
            plug = self._object.find_attribute(constants.kResetGroup)
            plug_src = plug.source()
            self._reset = None if plug_src.isNull() else _factory.create(plug_src.node())
        return self._reset
    
    @property
    def type(self) -> str:
        return f"{self.__class__.__name__}_{self._type}"
