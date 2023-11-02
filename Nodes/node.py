from typing import List, Optional, Union

from maya import cmds
from maya.api import OpenMaya

from HodoRig.Core import utils
from HodoRig.Builders.builder import Builder


class Node(Builder):

    def __init__(self, obj: Union[str, OpenMaya.MObject] = None):
        super().__init__()
        self._object = utils.check_object(obj) if obj else None
        self._parent = None
        self._children = []

    @property
    def object(self) -> Optional[OpenMaya.MObject]:
        return self._object
    
    @property
    def parent(self) -> Optional[OpenMaya.MObject]:
        return self._parent
    
    @property
    def children(self) -> List["Node"]:
        return self._children
    
    @property
    def name(self, full: bool = True, namespace: bool = True) -> str:
        return utils.name(self.object, full=full, namespace=namespace)
    
    @property
    def hash(self) -> str:
        return utils.node_hash(self.object)

    @classmethod
    def create(cls, *args, **kwargs):
        return cls(utils.create(*args, **kwargs))

    def is_valid(self) -> bool:
        if not self._object:
            return False
        return utils.is_valid(self._object)
    
    def set_parent(self, parent: Union[str, OpenMaya.MObject, "Node"]):
        if isinstance(parent, (str, OpenMaya.MObject)):
            parent = Node(parent)
        self._parent = parent
        cmds.parent(self.name, parent.name)
    
    def snap(self, ref_node: Union[str, OpenMaya.MObject, "Node"]):
        if isinstance(ref_node, (str, OpenMaya.MObject)):
            ref_node = Node(ref_node)
        cmds.matchTransform(self.name, ref_node.name)
