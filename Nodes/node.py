from __future__ import annotations
from typing import Union

from maya.api import OpenMaya

from HodoRig.Core import _factory, utils


class Node(object):

    def __new__(self, node: Union[str, OpenMaya.MObject]):
        return Node.get_node(node)
    
    @classmethod
    def create(cls, node_type: str, name: str = None,
                parent: OpenMaya.MObject = utils._nullObj) -> Node:
        new_node = utils.create(node_type, name, parent=parent)
        return Node.get_node(new_node)
    
    @classmethod
    def get_node(cls, node: str | OpenMaya.MObject):
        return _factory.create(node)
