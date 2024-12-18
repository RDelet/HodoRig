from __future__ import annotations
from typing import Optional

from maya import cmds
from maya.api import OpenMaya

from ..Core import constants as cst
from ..Core.nameBuilder import NameBuilder
from ..Helpers import utils
from ..Helpers.color import Color
from ..Nodes.node import Node
from ..Nodes.shape import Shape
from ..Builders.builder import Builder


class ManipulatorBuilder(Builder):

    def __init__(self, name: str | NameBuilder, manip_type: str = cst.kFk):
        super().__init__(name)

        self._type = manip_type
        self._reset = None
        self._node = None
    
    @property
    def node(self):
        return self._node

    @property
    def reset(self):
        return self._reset
    
    def _build(self, parent: OpenMaya.MObject = utils._nullObj,
               shape: str = "circle", shape_dir: int = None,
               scale: Optional[float] = None, color: Optional[Color] = None):
        super()._build()

        self._reset = Node.create("transform", name=self._name.clone(type="RESET"), parent=parent)
        self._node = Node.create("transform", self._name.clone(type="MANIP"), parent=self._reset)
        if color:
            self._node.apply_color(color)
        Shape.load(shape, self._node, shape_dir=shape_dir, scale=scale)

        self.__connect_nodes()
        self.__set_type()

    def __connect_nodes(self):
        self._node.add_attribute(cst.kResetGroup, cst.kMessage)
        self._reset.connect_to(cst.kMessage, f"{self._node}.{cst.kResetGroup}")

    def __set_type(self):
        self._node.add_attribute(cst.kManipulatorType, cst.kString)
        self._node.set_attribute(cst.kManipulatorType, self._type, lock=True)
