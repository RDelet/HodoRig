from __future__ import annotations
from typing import Optional

from maya import cmds
from maya.api import OpenMaya

from HodoRig.Core import _factory, utils
from HodoRig.Nodes._dgNode import _DGNode
from HodoRig.Nodes.node import Node


@_factory.register()
class _DAGNode(_DGNode):

    kApiType = OpenMaya.MFn.kDagNode

    def _post_init(self):
        self._mfn = OpenMaya.MFnDagNode(utils.get_path(self._object))
        self._modifier = OpenMaya.MDagModifier()
    
    @property
    def parent(self) -> Optional[OpenMaya.MObject]:
        parent = self._mfn.parent(0)
        return None if parent.hasFn(OpenMaya.MFn.kWorld) else Node.get_node(parent)
    
    @property
    def path(self):
        return utils.get_path(self._object)

    @parent.setter
    def parent(self, parent: str | OpenMaya.MObject | _DAGNode | None):
        if isinstance(parent, (str, OpenMaya.MObject)):
            parent = Node(parent)
        self._parent = parent
        if parent:
            cmds.parent(self.name, parent.name)
        else:
            cmds.parent(self.name, world=True)
    
    @property
    def children(self) -> list:
        children = []
        for i in range(self._mfn.childCount()):
            child = self._mfn.child(i)
            children.append(Node.get_node(child))

        return children
