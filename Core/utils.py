from typing import Union

from maya.api import OpenMaya


_msl = OpenMaya.MSelectionList()


def check_object(obj: Union[str, OpenMaya.MObject]) -> OpenMaya.MObject:
    if isinstance(obj, str):
        obj = get_object(obj)
    elif isinstance(obj, OpenMaya.MObject) and not is_valid(obj):
        raise RuntimeError("Invalid MObject !")
    return obj


def get_object(name: str) -> OpenMaya.MObject:
    """!@Brief Get MObject of current node."""

    try:
        _msl.clear()
        _msl.add(name)
        return _msl.getDependNode(0)
    except RuntimeError:
        raise RuntimeError(f"Node {name} does not exist !")


def name(obj: Union[OpenMaya.MObject, OpenMaya.MDagPath, OpenMaya.MPlug],
         full: bool = True, namespace: bool = True) -> str:
    """!@Brief Get node name."""
    if isinstance(obj, OpenMaya.MDagPath):
        name = obj.fullPathName()
    elif isinstance(obj, OpenMaya.MPlug):
        node_name = name(obj.node())
        attr_name = OpenMaya.MFnAttribute(obj.attribute()).name()
        name = f"{node_name}.{attr_name}"
    if isinstance(obj, OpenMaya.MObject):
        if not obj.hasFn(OpenMaya.MFn.kDagNode):
            name = OpenMaya.MFnDependencyNode(obj).name()
        else:
            name = OpenMaya.MFnDagNode(obj).fullPathName()
    else:
        raise TypeError(f"Argument must be a MObject not {type(obj)}")
    
    if not full:
        name = name.split('|')[-1]
    if not namespace:
        name = name.split(':')[-1]
    
    return name


def rename(node: Union[str, OpenMaya.MObject], new_name: str, force: bool = False):
    """!@Brief Rename given node."""
    if isinstance(node, str):
        node = get_object(node)

    mfn = OpenMaya.MFnDependencyNode(node)
    locked = mfn.isLocked
    if not force and locked:
        raise RuntimeError(f"Node {name(node)} is locked !")

    mfn.isLocked = False
    mdg_mod = OpenMaya.MDGModifier()
    mdg_mod.renameNode(node, new_name)
    mdg_mod.doIt()
    del mdg_mod
    mfn.isLocked = locked


def is_valid(node: Union[OpenMaya.MObject, OpenMaya.MDagPath]) -> bool:
    """!@Brief Check if node is valid."""
    if isinstance(node, OpenMaya.MDagPath):
        node = node.node()
    handle = OpenMaya.MObjectHandle(node)
    return not node.isNull() and handle.isAlive() and handle.isValid()
