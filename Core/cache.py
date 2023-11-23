import uuid
from typing import Union

from maya.api import OpenMaya

from HodoRig.Core import utils


class NodeCache:

    def __init__(self, enable: bool = True):
        self.enable: bool = enable
        self._cache = {}
        self._uuid1 = uuid.uuid1()

    def __str__(self) -> str:
        return self.__repr__()
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(count: {self.count})"

    def __eq__(self, other: "NodeCache"):
        return self._uuid1 == other._uuid1

    def __ne__(self, other: "NodeCache"):
        return self._uuid1 != other._uuid1
    
    def __len__(self) -> int:
        return self.count

    @property
    def count(self):
        return len(self._cache)
    
    @property
    def nodes(self) -> list:
        """!@Brief Returns the cache valid objects."""
        output = []
        for key, value in self._cache.items():
            if not utils.is_valid(value):
                self._cache.pop(key)
                continue
            output.append(value)

        return output
    
    def clear(self):
        """!@Brief  Clears the cache."""
        self._cache = {}

    def add(self, node: Union[str, OpenMaya.MObject, OpenMaya.MDagPath]):
        """!@Brief Add a new node to the cache."""
        if isinstance(node, str):
            node = utils.get_object(node)

        node_hash = utils.node_hash(node)
        if node_hash not in self._cache:
            self._cache[node_hash] = node

    def remove(self, node: Union[str, OpenMaya.MObject]):
        """!@Brief Removed a node from the cache."""
        if isinstance(node, str):
            node = utils.get_object(node)

        node_hash = OpenMaya.MObjectHandle_objectHashCode(node)
        if node_hash in self._cache:
            del self._cache[node_hash]
