from __future__ import annotations
from typing import Union

from maya.api import OpenMaya

from HodoRig.Core import _factory, utils


class Node(object):

    def __new__(self, node: Union[str, OpenMaya.MObject]):
        if isinstance(node, str):
            node = utils.get_object(node)
        return _factory.create(node)
    
    @classmethod
    def create(cls, node_type: str, name: str = None,
                parent: OpenMaya.MObject = utils._nullObj) -> Node:
        new_node = utils.create(node_type, name, parent=parent)
        return cls(new_node)
