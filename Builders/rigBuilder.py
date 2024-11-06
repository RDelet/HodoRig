from __future__ import annotations

from typing import List

from maya import cmds

from ..Core.logger import log
from ..Core import constants as cst
from ..Core.nameBuilder import NameBuilder
from ..Builders.builder import Builder
from ..Nodes.node import Node


class RigBuilder(Builder):

    def __init__(self, name: str | NameBuilder, sources: List[str], is_blended: bool = False):
        super().__init__(name)

        self._object = None
        self._sources = sources
        self._is_blended = is_blended

        self._manipulators = []
        self._output_blend = []

    def _check_validity(self):
        if not self._sources:
            raise RuntimeError("No sources setted !")

    def _pre_build(self):
        super()._pre_build()
        self._check_validity()
        self._build_node()

    def _post_build(self, *args, **kwargs):
        super()._post_build(*args, **kwargs)
        self._connect_manipulators()
    
    def _build_node(self):
        self._object = Node.create("network", self._name)
        cmds.addAttr(self._object.name, longName=cst.kManipulators, attributeType=cst.kMessage, multi=True)

    def _connect_manipulators(self):
        for i, manipulator in enumerate(self._manipulators):
            cmds.connectAttr(f"{manipulator.name}.{cst.kMessage}",
                             f"{self._object.name}.{cst.kManipulators}[{i}]", force=True)
