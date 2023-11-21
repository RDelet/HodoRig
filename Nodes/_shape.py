from __future__ import annotations

from maya import cmds
from maya.api import OpenMaya

from HodoRig.Nodes._dagNode import _DAGNode
from HodoRig.Nodes.node import Node


class _Shape(_DAGNode):

    kApiType = OpenMaya.MFn.kShape

    @_DAGNode.parent.setter
    def parent(self, parent: str | OpenMaya.MObject | _DAGNode):
        if isinstance(parent, (str, OpenMaya.MObject)):
            parent = Node(parent)
        self._parent = parent
        cmds.parent(self.name, parent.name, relative=True, shape=True)
