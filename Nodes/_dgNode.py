from __future__ import annotations
from typing import Optional

from maya.api import OpenMaya

from ..Helpers import utils

from ..Core import _factory


@_factory.register()
class _DGNode:

    kApiType = OpenMaya.MFn.kDependencyNode
    builder = None

    def __init__(self, node: Optional[str | OpenMaya.MObject] = None):
        if isinstance(node, _DGNode):
            node = node.object
        self._object = utils.check_object(node) if node else None
        self._mfn = None
        self._modifier = None
        if self._object:
            self._post_init()
    
    def _post_init(self):
        self._mfn = OpenMaya.MFnDependencyNode(self._object)
        self._modifier = OpenMaya.MDGModifier()

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name: {self.name}, type: {self.type})"
    
    @property
    def api_type(self) -> int:
        return self.object.apiType
    
    def find_attribute(self, attr: str, networked: bool = False) -> Optional[OpenMaya.MPlug]:
        try:
            return self._mfn.findPlug(attr, networked)
        except:
            return None

    def has_fn(self, fn: OpenMaya.MFn) -> bool:
        return self._object.hasFn(fn)
    
    def is_valid(self) -> bool:
        if not self._object:
            return False
        return utils.is_valid(self._object)

    @property
    def mfn(self):
        return self._mfn
    
    @property
    def modifier(self) -> OpenMaya.MDGModifier:
        return self._modifier

    @property
    def name(self):
        return utils.name(self._object)

    @property
    def object(self) -> OpenMaya.MObject:
        return self._object
    
    @property
    def short_name(self):
        return utils.name(self._object, False, False)
    
    @property
    def type(self) -> str:
        return self._mfn.typeName if self._mfn else None
