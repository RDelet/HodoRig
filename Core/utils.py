from __future__ import annotations

from maya import cmds
from maya.api import OpenMaya

from HodoRig.Core import apiUndo
from HodoRig.Core.component import SoftVertex


_dagMod = OpenMaya.MDagModifier()
_dgMod = OpenMaya.MDGModifier()
_msl = OpenMaya.MSelectionList()
_nullObj = OpenMaya.MObject.kNullObj

kDagNodeType = cmds.nodeType('dagNode', derived=True, isTypeName=True)

node_caches: list = []


def create(node_type: str, name: str = None, restriction: int = 0,
           parent: str | OpenMaya.MObject = _nullObj) -> OpenMaya.MObject:
    
    if isinstance(parent, str):
        parent = get_object(parent)

    is_dag = node_type in kDagNodeType
    if not is_dag and not is_valid(parent):
        raise RuntimeError("Impossible to set parent on dependency node !")

    modifier = _dagMod if node_type in kDagNodeType else _dgMod
    if node_type == "objectSet":
        new_node = OpenMaya.MFnSet().create(OpenMaya.MSelectionList(), restriction)
    else:
        new_node = modifier.createNode(node_type, parent)
    modifier.renameNode(new_node, name if name else f"{node_type}1")
    modifier.doIt()

    apiUndo.commit(modifier.undoIt, modifier.doIt)

    if node_caches:
        [cache.add(new_node) for cache in node_caches]

    return new_node


def check_object(obj: str | OpenMaya.MObject) -> OpenMaya.MObject:
    if isinstance(obj, str):
        obj = get_object(obj)
    elif isinstance(obj, OpenMaya.MObject) and not is_valid(obj):
        raise RuntimeError("Invalid MObject !")
    return obj


def get_object(node: str) -> OpenMaya.MObject:
    """!@Brief Get MObject of current node."""

    try:
        _msl.clear()
        _msl.add(node)
        return _msl.getDependNode(0)
    except RuntimeError:
        raise RuntimeError(f"Node {node} does not exist !")


def get_path(node: str | OpenMaya.MObject) -> OpenMaya.MDagPath:
    if isinstance(node, OpenMaya.MObject):
        if not node.hasFn(OpenMaya.MFn.kDagNode):
            raise RuntimeError(f"Node {name(node)} is not a dagNode !")
        return OpenMaya.MDagPath.getAPathTo(node)
    
    try:
        _msl.clear()
        _msl.add(node)
        return _msl.getDagPath(0)
    except RuntimeError:
        raise RuntimeError(f"Node {node} does not exist !")


def get_handle(node: str | OpenMaya.MObject) -> OpenMaya.MObjectHandle:
    """!@Brief Get MObjectHandle of current node."""
    if isinstance(node, str):
        node = get_object(node)

    return OpenMaya.MObjectHandle(node)


def name(obj: str | OpenMaya.MObject | OpenMaya.MPlug,
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


def node_hash(node: str | OpenMaya.MObject) -> str:
    handle = get_handle(node)
    return "%x" % handle.hashCode()


def rename(node: str | OpenMaya.MObject, new_name: str, force: bool = False):
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


def is_valid(obj: OpenMaya.MObject |OpenMaya.MObjectHandle) -> bool:
    if isinstance(obj, OpenMaya.MObject):
        node = obj
        handle = get_handle(obj)
    else:
        handle = obj
        node = handle.object()
        
    return not node.isNull() and handle.isValid() and handle.isAlive()


def soft_selection_weights() -> list:

    mrs = OpenMaya.MGlobal.getRichSelection()
    msl = mrs.getSelection()

    mit = OpenMaya.MItSelectionList(msl, OpenMaya.MFn.kMeshVertComponent)
    soft_vertices = []
    while not mit.isDone():
        path, component = mit.getComponent()
        if not path.hasFn(OpenMaya.MFn.kMesh):
            raise RuntimeError("Only mesh is implemented yet !")

        single_component = OpenMaya.MFnSingleIndexedComponent(component)
        for i in range(single_component.elementCount):
            weight = 1.0
            if single_component.hasWeights:
                weight = single_component.weight(i).influence
            soft_vertex = SoftVertex(path.fullPathName(), single_component.element(i), weight)
            soft_vertices.append(soft_vertex)

        mit.next()

    return soft_vertices
