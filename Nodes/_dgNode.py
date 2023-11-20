from __future__ import annotations
from typing import Optional

from maya.api import OpenMaya

from HodoRig.Core import _factory, utils


@_factory.register()
class _DGNode:

    kApiType = OpenMaya.MFn.kDependencyNode

    def __init__(self, node: str | OpenMaya.MObject):
        self._object = utils.check_object(node)
        self._mfn = None
        self._modifier = None
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
        return self.object.apiTypeStr
    
    def is_valid(self) -> bool:
        if not self._object:
            return False
        return utils.is_valid(self._object)
    
    def find_attribute(self, attr: str, networked: bool = False) -> Optional[OpenMaya.MPlug]:
        try:
            return self._mfn.findPlug(attr, networked)
        except:
            return None
