from __future__ import annotations

from maya import cmds
from maya.api import OpenMaya

from ..Helpers import utils
from ..Builders.rigBuilder import RigBuilder
from .manipulator import Manipulator


# ToDo: Create factory
class IK(RigBuilder):

    def _check_validity(self):
        super()._check_validity()
        if len(self._sources) < 2:
            raise RuntimeError("IK builder need to have 2 sources minimum !")

    def _build(self, parent: OpenMaya.MObject = utils._nullObj):
        super()._build()
        
        pass

    def _duplicate_sources(self):
