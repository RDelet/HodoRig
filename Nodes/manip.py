from __future__ import annotations
from typing import Union

from maya.api import OpenMaya

from HodoRig.Core import builder
from HodoRig.Core.nameBuilder import NameBuilder
from HodoRig.Core.logger import log
from HodoRig.Nodes._transformNode import _TransformNode
from HodoRig.Nodes.node import Node
from HodoRig.Nodes._shape import _Shape


class Manip(_TransformNode, builder.Builder):

    def __init__(self, node: str | OpenMaya.MObject = None):
        super().__init__(node)

        self._reset = None
        self._type = None
        self._shape = None
    
    def _pre_build(self, *args, **kwargs):
        log.debug(f"{self.__class__.__name__} {self._base_name} build: {self._base_name}.")

    def _build(self, name: str | NameBuilder, shape: str = "circle",
               shape_dir: int = None, scale: float = None):
        log.debug(f"{self.__class__.__name__} build: {name}.")
        if isinstance(name, str):
            name = NameBuilder.from_name(name)

        reset_name = f"RESET_{self._base_name}"
        manip_name = f"MANIP_{self._base_name}"

        self._parent = Node.create("transform", name=reset_name)
        manip = Node.create("transform", name=manip_name, parent=self._parent.name)
        self._object = manip.object

        self._shape = _Shape.load(shape, manip.object)
    
    def _post_build(self, *args, **kwargs):
        log.debug(f"{self.__class__.__name__} post build: {self._base_name}")
    
    def set_parent(self, parent: str | OpenMaya.MObject | _TransformNode):
        if not isinstance(parent, _TransformNode):
            parent = Node.get_node(parent)
        self.parent.set_parent(parent)