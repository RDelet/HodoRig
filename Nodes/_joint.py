from __future__ import annotations

from maya.api import OpenMaya

from ..Core import _factory
from ..Nodes._transformNode import _TransformNode

@_factory.register()
class _Joint(_TransformNode):

    kApiType = OpenMaya.MFn.kJoint

    # ToDo
