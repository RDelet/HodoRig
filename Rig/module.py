"""!@Brief Module builder.
           Select joints and launch this code

from HodoRig.Rig.module import Module
from HodoRig.Nodes.node import Node


sources = Node.selected(node_type="joint")
module = Module("L_0_Groot", sources)
module.build()
"""

from __future__ import annotations
from typing import List

from ..Core import constants as cst
from ..Core.nameBuilder import NameBuilder
from ..Builders.builder import Builder
from ..Builders.builderState import BuilderState
from ..Nodes.node import Node
from .rigBuilder import RigBuilder


class Module(Builder):

    def __init__(self, name: str | NameBuilder, sources: List[str]):
        super().__init__(name)

        self._builders = []
        self._children = []

        self._object = None
        self._sources = sources

    def _pre_build(self, *args, **kwargs):
        super()._pre_build(*args, **kwargs)
    
        self.check_validity()
        self._build_nodes()
        self._build_attributes()
    
    def _build(self, *args, **kwargs):
        super()._build(*args, **kwargs)

        for builder in self._builders:
            builder.build()
    
    def _post_build(self, *args, **kwargs):
        super()._post_build(*args, **kwargs)
        self._connect_builders()
        for child in self._children:
            child.build()
    
    def _build_nodes(self):
        self._object = Node.create("network", self._name)

    def _build_attributes(self):
        self._object.add_attribute(cst.kBuilders, cst.kMessage, multi=True)
        self._object.add_attribute(cst.kParent, cst.kMessage)
    
    def _connect_builders(self):
        for i, child in enumerate(self._builders):
            self._object.connect_to(f"{cst.kBuilders}[{i}]", f"{child.object}.{cst.kParent}")
    
    def add_builder(self, builder: RigBuilder):
        if not isinstance(builder, RigBuilder):
            raise RuntimeError("Argument must be a RigBuilder !")
        if builder in self._builders:
            raise RuntimeError(f"Builder {builder.name} already in module !")
        
        self._builders.append(builder)
        builder._sources = self._sources
        builder.name = self.name.clone(type=builder.__class__.__name__)

    def check_validity(self):
        if not self._sources:
            raise RuntimeError("No sources setted !")
        if not self._builders:
            raise RuntimeError("No builders setted !")
        
        for builder in self._builders:
            builder.check_validity()
    
    def to_dict(self) -> dict:
        raise NotImplementedError("Module.to_dict not implemented yet !")

    def from_dict(self) -> dict:
        raise NotImplementedError("Module.from_dict not implemented yet !")
