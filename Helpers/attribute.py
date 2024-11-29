from maya import cmds


def exists(node: str, attribute: str) -> bool:
    """!@Brief Check if attribut exists.

               I use objExists and attributeQuery because with few case one or the other doesn't work.
               Exemple: MANIP_L_0_Shoulder.-- SHOULDER SETTINGS --
                        In this case objExists return False but attributeQuery return True.
               Exemple: MANIP_L_0_Shoulder.translate.translateX
                        In this exemple objExists return True but attributeQuery return False.
    """
    attr_exists = cmds.objExists(f"{node}.{attribute}")
    if not attr_exists:
        attr_exists = cmds.attributeQuery(attribute, node=node, exists=True)

    return attr_exists


def duplicate_from_node(source_node: str, target_node: str):
    """!@Brief Duplicate dynamique attribute from other node."""
    custom_attrs = cmds.listAttr(source_node, userDefined=True) or []
    for attr in custom_attrs:
        source_attr = f"{source_node}.{attr}"
        if not cmds.attributeQuery(attr, node=target_node, exists=True):
            cmds.addAttr(target_node, longName=attr, attributeType=cmds.getAttr(source_attr, type=True))
        cmds.setAttr(f"{target_node}.{attr}", cmds.getAttr(source_attr))