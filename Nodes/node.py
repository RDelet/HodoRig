from __future__ import annotations
from typing import Optional

from maya import cmds
from maya.api import OpenMaya

from ..Core import _factory, constants
from ..Core.logger import log
from ..Helpers import attribute, utils


@_factory.register()
class Node:

    kApiType = OpenMaya.MFn.kDependencyNode
    builder = None

    def __init__(self, node: Optional[str | OpenMaya.MObject] = None):
        if isinstance(node, Node):
            node = node.object
        self._handle = utils.get_handle(node) if node else None
        self._mfn = None
        self._modifier = None
        if self._handle:
            self._post_init()
    
    def _post_init(self):
        self._mfn = OpenMaya.MFnDependencyNode(self.object)
        self._modifier = OpenMaya.MDGModifier()

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return str(self.name)
    
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
        return utils.name(self.object)

    @property
    def object(self) -> OpenMaya.MObject:
        return self._handle.object() if self._handle else None
    
    @property
    def short_name(self):
        return utils.name(self.object, False, False)
    
    @property
    def type(self) -> str:
        return self._mfn.typeName if self._mfn else None
    
    @classmethod
    def create(cls, node_type: str, name: str = None,
                parent: OpenMaya.MObject | Node = None) -> Node:
        if isinstance(parent, Node):
            parent = parent.object
        new_node = utils.create(node_type, name, parent=parent)
        return cls.get(new_node)
    
    @classmethod
    def get(cls, node: str | OpenMaya.MObject):
        return _factory.create(node)
    
    def rename(self, new_name: str, force: bool = False):
        utils.rename(self.object, new_name, force)
    
    @classmethod
    def selected(cls, node_type: Optional[str | list | tuple] = None):
        kwargs = {}
        if node_type is not None:
            kwargs["type"] = node_type
        return [cls.get(x) for x in cmds.ls(selection=True, long=True, flatten=True, **kwargs)]
    
    def duplicate(self, name: Optional[str] = None) -> Node:
        if name is None:
            name = f"DUP_{self.short_name}"
        new_node = self.create(self.type, name=name)
        # ToDo:
        # attr.duplicate_from_node(self.name, new_node.name)

        return new_node
    
    def add_attribute(self, name: str, attr_type: str, **kwargs):
        if attribute.exists(self, name):
            log.warning(f"Attirbute {name} already exists on {self}.")
            return

        if attr_type in constants.kAttributeTypes:
            cmds.addAttr(self, longName=name, attributeType=attr_type, **kwargs)
        else:
            cmds.addAttr(self, longName=name, dataType=attr_type, **kwargs)
    
    def add_settings_attribute(self, attr_name: str):
        cmds.addAttr(self, longName=attr_name, attributeType="enum", enumName="-----")
        cmds.setAttr(f"{self}.{attr_name}", channelBox=True, lock=True)
    
    def get_attribute(self, attr_name: str, **kwargs):
        if not attribute.exists(self, attr_name):
            raise RuntimeError(f"Attirbute {attr_name} does not exists on {self}.")
        
        return cmds.getAttr(f"{self}.{attr_name}", **kwargs)

    def set_attribute(self, attr_name: str, value: str | int | float | bool | list | tuple, **kwargs):
        if not attribute.exists(self, attr_name):
            raise RuntimeError(f"Attirbute {attr_name} does not exists on {self}.")

        node_attr = f"{self}.{attr_name}"
        if isinstance(value, str):
            cmds.setAttr(node_attr, value, type=constants.kString)
        elif isinstance(value, (list, tuple)) and len(value) == 16:
            cmds.setAttr(node_attr, value, type=constants.kMatrix)
        elif isinstance(value, (OpenMaya.MMatrix, OpenMaya.MFloatMatrix)):
            cmds.setAttr(node_attr, value, type=constants.kMatrix)
        else:
            if isinstance(value, list):
                is_array = cmds.attributeQuery(attr_name, node=self, multi=True)
                children = cmds.attributeQuery(attr_name, node=self, listChildren=True)
                if is_array:
                    for i, v in enumerate(value):
                        cmds.setAttr(f"{node_attr}[{i}]", v)
                elif children:
                    for i, child in enumerate(children):
                        cmds.setAttr(f"{node_attr}.{child}", value[i])
                elif is_array and children:
                    raise RuntimeError("Set counpound array not implemented yet !")
            else:
                cmds.setAttr(node_attr, value)
    
    def connect_to(self, src_attr: str, dst_attr: str):
        if not attribute.exists(self, src_attr):
            raise RuntimeError(f"Attirbute {src_attr} does not exists on {self}.")
        cmds.connectAttr(f"{self}.{src_attr}", dst_attr, force=True)

    def has_fn(self, fn: OpenMaya.MFn) -> bool:
        return self.object.hasFn(fn)
    
    def is_valid(self) -> bool:
        return utils.is_valid(self.object) if self._handle else False
