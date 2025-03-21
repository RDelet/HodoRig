from __future__ import annotations
from typing import List, Optional

from ..Core import constants as cst
from ..Core.nameBuilder import NameBuilder
from ..Helpers import utils
from ..Builders.builder import Builder
from ..Nodes.node import Node


class RigBuilder(Builder):

    def __init__(self, name: Optional[str | NameBuilder] = NameBuilder(),
                 sources: Optional[List[Node]]= []):
        super().__init__(name)

        self._name.type = self.__class__.__name__

        self._parent_grp = None
        self._object = None
        self._sources = sources
        self._is_blended = False

        self._manipulators = []
        self._output_blend = []

    def _get_settings(self):
        pass

    def check_validity(self):
        if not self._sources:
            raise RuntimeError("No sources setted !")

    def _pre_build(self, *args, parent: Optional[str | Node] = None, **kwargs):
        super()._pre_build(*args, **kwargs)

        self._parent_grp = parent
        self._manipulators = []
        self._output_blend = []

        self._get_settings()
        self.check_validity()
        self._build_nodes()
        self._build_attributes()

    def _post_build(self, *args, **kwargs):
        super()._post_build(*args, **kwargs)
        self._connect_manipulators()
        self._connect_builders()
    
    def _build_nodes(self):
        self._object = Node.create(cst.kNetwork, self._name)

    def _build_attributes(self):
        self._object.add_attribute(cst.kManipulators, cst.kMessage, multi=True)
        self._object.add_attribute(cst.kBuilders, cst.kMessage, multi=True)
        self._object.add_attribute(cst.kParent, cst.kMessage)

    def _connect_manipulators(self):
        for i, manipulator in enumerate(self._manipulators):
            manipulator.connect_to(cst.kMessage, f"{self._object.name}.{cst.kManipulators}[{i}]")
    
    def _connect_builders(self):
        for i, child in enumerate(self._children):
            self._object.connect_to(f"{cst.kBuilders}[{i}]", f"{child.object}.{cst.kParent}")
    
    def add_children(self, builder):
        super().add_children(builder)
        builder._sources = self._sources
        builder.name = self.name.clone(type=builder.__class__.__name__)

    def set_sources(self, sources: List[Node]):
        self._sources = sources

    @property
    def is_blended(self) -> bool:
        return self._is_blended
    
    @property
    def object(self) -> Node:
        return self._object
    
    def to_dict(self) -> dict:
        raise NotImplementedError("Module.to_dict not implemented yet !")

    def from_dict(self) -> dict:
        raise NotImplementedError("Module.from_dict not implemented yet !")
