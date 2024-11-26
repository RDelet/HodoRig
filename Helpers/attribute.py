from maya import cmds



def duplicate_from_node(source_node: str, target_node: str):
    """!@Brief Duplique tous les attributs custom d'un noeud Maya source sur un noeud cible."""
    custom_attrs = cmds.listAttr(source_node, userDefined=True) or []
    for attr in custom_attrs:
        source_attr = f"{source_node}.{attr}"
        if not cmds.attributeQuery(attr, node=target_node, exists=True):
            cmds.addAttr(target_node, longName=attr, attributeType=cmds.getAttr(source_attr, type=True))
        cmds.setAttr(f"{target_node}.{attr}", cmds.getAttr(source_attr))