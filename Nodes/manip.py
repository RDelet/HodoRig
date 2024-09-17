from __future__ import annotations

from maya.api import OpenMaya

from ..Core import constants, utils
from ..Core.nameBuilder import NameBuilder
from ..Core.builder import Builder
from ..Nodes._transformNode import _TransformNode
from ..Nodes.node import Node
from ..Nodes._shape import _Shape


class Manip(_TransformNode, Builder):

    def __init__(self, node: str | OpenMaya.MObject = None):
        _TransformNode.__init__(self, node=node)
        Builder.__init__(self)

        self._reset = None
        self._type = None
    
    @property
    def reset(self) -> _TransformNode:
        return self._reset
    
    @property
    def type(self) -> str:
        return self._type

    def _build(self, name: str | NameBuilder, shape: str = "circle",
               shape_dir: int = None, scale: float = None, manip_type: str = constants.kFk):
        super()._build()

        if isinstance(name, str):
            name = NameBuilder.from_name(name)

        self._reset = Node.create("transform", name=name.clone(type="RESET"))
        self._object = utils.create("transform", name.clone(type="MANIP"), parent=self._reset.object)
        self._shapes = _Shape.load(shape, self._object, shape_dir=shape_dir, scale=scale)
        self._type = manip_type
        self._post_init()
    
    def set_parent(self, parent: str | OpenMaya.MObject | _TransformNode):
        self._reset.set_parent(parent)
