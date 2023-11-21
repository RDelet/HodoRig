from __future__ import annotations
import inspect
import copy
import six
from typing import Any, TypeVar

from maya.api import OpenMaya

from HodoRig.Core import _instances, utils
from HodoRig.Core.logger import log


ClassType = TypeVar("ClassType", bound="BaseClass")
_registered = dict()


def create(node: OpenMaya.MObject) -> Any:
    instance = _instances.get(node)
    return instance if instance else _create(node)


def _create(node: str | OpenMaya.MObject):
    if isinstance(node, str):
        node = utils.get_object(node)

    api_type = _get_type(node)
    if not is_registered(api_type):
        raise RuntimeError(f"Type {node.apiTypeStr} not registered !")
    new_cls = _registered[api_type](node)
    _instances.add(node, new_cls)

    return new_cls


def _get_type(node: OpenMaya.MObject):
    api_type = node.apiType()
    if not is_registered(api_type):
        if node.hasFn(OpenMaya.MFn.kShape):
            api_type = OpenMaya.MFn.kShape
        elif node.hasFn(OpenMaya.MFn.kDagNode):
            api_type = OpenMaya.MFn.kDagNode
        else:
            api_type = OpenMaya.MFn.kDependencyNode
    
    return api_type


def register():
    def do_register(class_obj: ClassType):
        if not inspect.isclass(class_obj):
            raise RuntimeError("This decorator can be use only by a class !")
        _do_register(class_obj)
        return class_obj
    return do_register


def _do_register(class_obj: ClassType):
    api_type = class_obj.kApiType
    if is_registered(api_type):
        log.debug(f"Class {class_obj.__name__} already registered.")
        return

    _registered[api_type] = class_obj
    log.debug(f"Class {class_obj.__name__} registered.")


def is_registered(api_type: int) -> bool:
    return api_type in _registered


def registered() -> dict:
    return copy.copy(_registered)
