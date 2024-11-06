from __future__ import annotations
from typing import Optional

from maya import cmds
from maya.api import OpenMaya

from ..Core import _factory
from ..Helpers import utils
from ..Nodes._dgNode import _DGNode


class Node:

    def __new__(self, node: str |  OpenMaya.MObject):
        return Node.get(node)
    
    @classmethod
    def create(cls, node_type: str, name: str = None,
                parent: OpenMaya.MObject | _DGNode = utils._nullObj) -> Node:
        if isinstance(parent, _DGNode):
            parent = parent.object
        new_node = utils.create(node_type, name, parent=parent)
        return Node.get(new_node)
    
    @classmethod
    def get(cls, node: str | OpenMaya.MObject):
        return _factory.create(node)
    
    @classmethod
    def selected(cls, node_type: Optional[str | list | tuple] = None):
        kwargs = {}
        if node_type is not None:
            kwargs["type"] = node_type
        return [cls.get(x) for x in cmds.ls(selection=True, long=True, flatten=True, **kwargs)]
