from __future__ import annotations
from typing import Optional

from maya import cmds
from maya.api import OpenMaya

from ..Core import _factory
from ..Core.logger import log
from ..Helpers import utils
from ..Helpers.color import Color
from .node import Node


@_factory.register()
class DAGNode(Node):

    kApiType = OpenMaya.MFn.kDagNode

    def _post_init(self):
        self._mfn = OpenMaya.MFnDagNode(utils.get_path(self._object))
        self._modifier = OpenMaya.MDagModifier()

    def duplicate(self, name: Optional[str] = None, parent: Optional[str | DAGNode] = None) -> DAGNode:
        new_node = super().duplicate(name=name)
        if parent is not None:
            if isinstance(parent, (str, OpenMaya.MObject)):
                parent = self.get(parent)
            if parent.is_valid():
                new_node.parent = parent

        return new_node
    
    @property
    def path(self):
        return utils.get_path(self._object)

    @property
    def parent(self) -> Optional[OpenMaya.MObject]:
        parent = self._mfn.parent(0)
        return None if parent.hasFn(OpenMaya.MFn.kWorld) else self.get(parent)

    @parent.setter
    def parent(self, parent: str | OpenMaya.MObject | DAGNode | None):
        if isinstance(parent, (str, OpenMaya.MObject)):
            parent = self(parent)
        self._parent = parent
        if parent:
            cmds.parent(self.name, parent.name)
        else:
            cmds.parent(self.name, world=True)
    
    def children(self, type: Optional[str] = None) -> list:
        children = []
        for i in range(self._mfn.childCount()):
            child = self.get(self._mfn.child(i))
            if type and child.type != type:
                continue
            children.append(child)

        return children

    def apply_color(self, color: Color):
        try:
            cmds.setAttr(f"{self.name}.overrideEnabled", True)
            cmds.setAttr(f"{self.name}.overrideColor", color.maya_index)
        except:
            log.debug(f"Impossible to set color on {self.name}.")
    
    def apply_rgb_color(self, color: Color):
        raise NotImplemented("Methode apply_rgb_color not implemented yet !")
