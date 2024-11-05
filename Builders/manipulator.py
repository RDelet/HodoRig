from __future__ import annotations

from maya import cmds
from maya.api import OpenMaya

from ..Core import constants
from ..Core.nameBuilder import NameBuilder
from .builder import Builder
from ..Helpers import utils

from ..Nodes.node import Node
from ..Nodes._shape import _Shape

class Manipulator(Builder):

    def __init__(self, name: str | NameBuilder, manip_type: str = constants.kFk):
        super().__init__()

        self._name = NameBuilder.from_name(name) if isinstance(name, str) else name
        self._type = manip_type
        self._reset = None
        self._node = None
    
    @property
    def node(self):
        return self._node

    @property
    def reset(self):
        return self._reset
    
    def _build(self, shape: str = "circle", shape_dir: int = None, scale: float = None):
        super()._build()

        self.__build(shape, shape_dir, scale)
        self.__connect_nodes()
        self.__set_classname()
        self.__set_type()

    def __build(self, parent: OpenMaya.MObject = utils._nullObj,
                shape: str = "circle", shape_dir: int = None, scale: float = None):
        self._reset = Node.create("transform", name=self._name.clone(type="RESET"), parent=parent)
        self._node = Node.create("transform", self._name.clone(type="MANIP"), parent=self._reset.object)
        _Shape.load(shape, self._node.object, shape_dir=shape_dir, scale=scale)

    def __connect_nodes(self):
        cmds.addAttr(self._node.name, longName=constants.kResetGroup,
                     attributeType=constants.kMessage)
        cmds.connectAttr(f"{self._reset.name}.{constants.kMessage}",
                         f"{self._node.name}.{constants.kResetGroup}", force=True)

    def __set_classname(self):
        cmds.addAttr(self._node.name, longName=constants.kClassName,
                     dataType=constants.kString)
        cmds.setAttr(f"{self._node.name}.{constants.kManipulatorType}", self.__class__.__name__,
                     type=constants.kString)

    def __set_type(self):
        cmds.addAttr(self._node.name, longName=constants.kManipulatorType,
                     dataType=constants.kString)
        cmds.setAttr(f"{self._node.name}.{constants.kManipulatorType}", self._type,
                     type=constants.kString)
