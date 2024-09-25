from __future__ import annotations
from typing import Optional

from maya import cmds
from maya.api import OpenMaya

from ..Helpers import utils

from ..Core import constants
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

        reset = Node.create("transform", name=name.clone(type="RESET"))
        object = utils.create("transform", name.clone(type="MANIP"), parent=self._reset.object)
        shapes = _Shape.load(shape, self._object, shape_dir=shape_dir, scale=scale)

        cmds.addAttr(object.name, longName="resetGroup", dataType="message")
        cmds.connectAttr(f"{reset.name}.message", f"{object.name}.resetGroup", force=True)

        manip = Manip(object, type=manip_type, shape=shapes)

        return manip


class Manip(_TransformNode):

    builder = ManipBuilder()

    def __init__(self, node: Optional[str | OpenMaya.MObject] = None,
                 type: Optional[str] = None, shape: Optional[list | tuple] = None):
        super().__init__(self, node=node)

        self._reset = None
        self._shapes = None
        self._type = type
    
    @property
    def reset(self) -> _TransformNode:
        return self._reset
    
    @property
    def type(self) -> str:
        return f"{self.__class__.__name__}_{self._type}"
