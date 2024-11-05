from typing import List

from ..Core.logger import log
from ..Builders.builder import Builder


class RigBuilder(Builder):

    def __init__(self, sources: List[str], is_blended: bool = False):
        super().__init__()

        self._sources = sources
        self._is_blended = is_blended
        self._manipulators = []
        self._output_blend = []

    def _check_validity(self):
        if not self._sources:
            raise RuntimeError("No sources setted !")

    def _pre_build(self, *args, **kwargs):
        super()._pre_build(*args, **kwargs)

        self._check_validity()
        self._build_node()

    def _post_build(self, *args, **kwargs):
        super()._post_build(*args, **kwargs)

        self._connect_manipulators()
    
    def _build_node(self):
        pass

    def _connect_manipulators(self):
        pass