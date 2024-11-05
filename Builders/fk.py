from __future__ import annotations

from typing import List

from ..Helpers import utils
from ..Builders.builder import Builder
from .manipulator import Manipulator


class FK(Builder):

    def __init__(self, sources: List[str]):
        super().__init__()

        self._sources = sources
        self._manipulators = []
        self._output_blend = []
    
    def _check_validity(self):
        if not self._sources:
            raise RuntimeError("No sources setted !")

    def _pre_build(self, *args, **kwargs):
        super()._pre_build(*args, **kwargs)

    def _build(self, *args, **kwargs):
        super()._build(*args, **kwargs)
        
        parent = utils._nullObj
        for jnt in self._sources:
            builder = Manipulator(jnt.split("|")[-1].split(":")[-1])
            builder.build(parent, shape="circle", shape_dir=0, scale=30.0)
            builder.reset.snap(jnt)
            parent = builder.node.object
            self._manipulators.append(builder.node)
    
    def _post_build(self, *args, **kwargs):
        super()._post_build(*args, **kwargs)
        self._output_blend = self._manipulators