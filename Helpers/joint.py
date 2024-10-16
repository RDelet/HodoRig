from maya import cmds
from maya.api import OpenMaya

# from ..Helpers import utils  # ToDO: Do type_of


def reste_bind_matrix(jnt: str, recursive: bool = True):
    if not cmds.objExists(jnt):
        raise RuntimeError(f"Node {jnt} does not exists !")
    node_type = cmds.nodeType(jnt)
    if not node_type == "joint":
        raise RuntimeError(f"node must be a joint not {node_type} !")

    jnt_matrix = OpenMaya.MMatrix(cmds.xform(jnt, query=True, matrix=True, worldSpace=True))
    cmds.setAttr(f"{jnt}.bindPose", jnt_matrix, type='matrix')

    destinations = cmds.listConnections(f"{jnt}.worldMatrix[0]", source=False, destination=True, type="skinCluster", plugs=True) or []
    for dst in destinations:
        skin_node, attr = dst.split(".")
        matrix_id = (attr.split("[")[-1].split("]")[0])
        cmds.setAttr(f"{skin_node}.bindPreMatrix[{matrix_id}]", jnt_matrix.inverse(), type="matrix")

    if recursive:
        children = cmds.listRelatives(jnt, children=True, type="joint", fullPath=True) or []
        for child in children:
            reste_bind_matrix(child, recursive=recursive)


def go_to_bindpose(jnt: str, recursive: bool = True):
    if not cmds.objExists(jnt):
        raise RuntimeError(f"Node {jnt} does not exists !")
    node_type = cmds.nodeType(jnt)
    if not node_type == "joint":
        raise RuntimeError(f"node must be a joint not {node_type} !")

    bindpose = cmds.getAttr(f"{jnt}.bindPose")
    if bindpose:
        cmds.xform(jnt, matrix=bindpose, worldSpace=True)

    if recursive:
        children = cmds.listRelatives(jnt, children=True, type="joint", fullPath=True) or []
        for child in children:
            go_to_bindpose(child, recursive=recursive)
