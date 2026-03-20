import numpy as np

from maya import cmds
from maya.api import OpenMaya as om


def clean_skin(node: str):
    skin_nodes = [x for x in cmds.listHistory(node) if cmds.nodeType(x) == "skinCluster"]
    if not skin_nodes:
        return

    skin_node = skin_nodes[0]
    shapes = cmds.skinCluster(skin_node, query=True, geometry=True)
    if not shapes:
        raise RuntimeError(f"Skin {skin_node} does not have output geometry !")

    shape = shapes[0]
    influences = cmds.skinCluster(skin_node, query=True, influence=True)
    influence_matrix = [cmds.xform(x, query=True, matrix=True, worldSpace=True) for x in influences]
    influence_ids = cmds.getAttr(f"{skin_node}.matrix", multiIndices=True)
    vtx_count = len(cmds.ls(f"{shape}.vtx[*]", flatten=True))
    influence_count = len(influences)

    # Get Weight
    weights = np.zeros((vtx_count, influence_count))
    for i in range(vtx_count):
        w = []
        for j, inf_id in enumerate(influence_ids):
            w.append(cmds.getAttr(f"{skin_node}.weightList[{i}].weights[{inf_id}]"))
        weights[i] = np.array(w)

    # Clean
    for inf_id in reversed(influence_ids):
        inputs = cmds.listConnections(f"{skin_node}.matrix[{inf_id}]", source=True, destination=False)
        if inputs:
            cmds.disconnectAttr(f"{inputs[0]}.worldMatrix[0]", f"{skin_node}.matrix[{inf_id}]")
        cmds.removeMultiInstance(f"{skin_node}.bindPreMatrix[{inf_id}]")
        cmds.removeMultiInstance(f"{skin_node}.matrix[{inf_id}]")

    for i in reversed(range(vtx_count)):
        cmds.removeMultiInstance(f"{skin_node}.weightList[{i}]")

    # Set
    for i in range(influence_count):
        influence = influences[i]
        cmds.connectAttr(f"{influence}.worldMatrix[0]", f"{skin_node}.matrix[{i}]")
        inv_matrix = om.MMatrix(influence_matrix[i]).inverse()
        cmds.setAttr(f"{skin_node}.bindPreMatrix[{i}]", inv_matrix, type="matrix")

    for i in range(vtx_count):
        for j in range(influence_count):
            cmds.setAttr(f"{skin_node}.weightList[{i}].weights[{j}]", weights[i][j])


meshes = cmds.ls(type="mesh", long=True)
for mesh in meshes:
    node = cmds.listRelatives()
    clean_skin(node)