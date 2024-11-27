from __future__ import annotations
from typing import List, Optional

from ...Core import constants as cst
from ...Core.nameBuilder import NameBuilder
from ...Helpers import utils
from ..builder import Builder
from ...Nodes.node import Node


class RigBuilder(Builder):

    def __init__(self, name: str | NameBuilder, sources: List[str], is_blended: bool = False):
        super().__init__(name)

        self._name.type = self.__class__.__name__

        self._object = None
        self._sources = sources
        self._is_blended = is_blended

        self._rig_group = None
        self._build_rig_group = True
        self._sub_builders = []
        self._manipulators = []
        self._output_blend = []

    def _get_settings(self):
        pass

    def _check_validity(self):
        if not self._sources:
            raise RuntimeError("No sources setted !")

    def _pre_build(self, parent: Optional[str | Node] = utils._nullObj):
        super()._pre_build()

        self._manipulators = []
        self._output_blend = []

        self._get_settings()
        self._check_validity()
        self._build_nodes(parent)

    def _post_build(self, *args, **kwargs):
        super()._post_build(*args, **kwargs)
        self._connect_manipulators()
    
    def _build_nodes(self, parent: Optional[str | Node] = utils._nullObj):
        self._object = Node.create("network", self._name)
        self._object.add_attribute(cst.kManipulators, cst.kMessage, multi=True)
        if self._build_rig_group:
            self._rig_group = Node.create("transform", name=f"RIG_{self.name}", parent=parent)

    def _connect_manipulators(self):
        for i, manipulator in enumerate(self._manipulators):
            manipulator.connect_to(cst.kMessage, f"{self._object.name}.{cst.kManipulators}[{i}]")
    
    @property
    def is_blended(self) -> bool:
        return self._is_blended
