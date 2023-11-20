from __future__ import annotations
from typing import Any

from maya.api import OpenMaya

from HodoRig.Core import utils


_instances = {}


def get(node: OpenMaya.MObject | OpenMaya.MDagPath) -> Any:
    handle = utils.get_handle(node)
    if utils.is_valid(handle):
        hx = utils.node_hash(handle)
        if hx in _instances:
            instance = _instances[hx]
            instance._object(node)
            return instance


def add(node: OpenMaya.MObject | OpenMaya.MDagPath, node_cls: Any):
    handle = utils.get_handle(node)
    if utils.is_valid(handle):
        hx = utils.node_hash(handle)
        if hx not in _instances:
            _instances[hx] = node_cls


def remove(node: OpenMaya.MObject | OpenMaya.MDagPath, *args, **kwargs):
    handle = utils.get_handle(node)
    if utils.is_valid(handle):
        hx = utils.node_hash(handle)
        if hx in _instances:
            del _instances[hx]
        


def _clear(*args, **kwargs):
    _instances = {}


OpenMaya.MDGMessage.addNodeRemovedCallback(remove, "node")  # node = all maya nodes
OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kMayaExiting, _clear)
OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kAfterNew, _clear)
