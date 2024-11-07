from __future__ import annotations
from typing import Optional

from maya import cmds
from maya.api import OpenMaya

from ..Core import constants as cst
from ..Core.nameBuilder import NameBuilder
from ..Builders.builder import Builder
from ..Helpers import utils
from ..Helpers.color import Color

from ..Nodes.node import Node
from ..Nodes._shape import _Shape


class Manipulator(Builder):

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
        _Shape.load(shape, self._node, shape_dir=shape_dir, scale=scale)

        self.__connect_nodes()
        self.__set_classname()
        self.__set_type()

    def __connect_nodes(self):
        cmds.addAttr(self._node.name, longName=cst.kResetGroup, attributeType=cst.kMessage)
        cmds.connectAttr(f"{self._reset.name}.{cst.kMessage}", f"{self._node.name}.{cst.kResetGroup}", force=True)

    def __set_classname(self):
        cmds.addAttr(self._node.name, longName=cst.kClassName, dataType=cst.kString)
        cmds.setAttr(f"{self._node.name}.{cst.kClassName}", self.__class__.__name__,
                     type=cst.kString, lock=True)

    def __set_type(self):
        cmds.addAttr(self._node.name, longName=cst.kManipulatorType, dataType=cst.kString)
        cmds.setAttr(f"{self._node.name}.{cst.kManipulatorType}", self._type,
                     type=cst.kString, lock=True)
