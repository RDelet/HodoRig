from maya import cmds

from HodoRig.Nodes.node import Node
from HodoRig.Nodes.manip import Manip
from HodoRig.Builders.builder import Builder


class Spine(Builder):

    def __init__(self):
        super().__init__()
    
    def _build(self):
        module_root = Node.create("transform", name="MOD_Root")
        skeleton_grp = Node.create("transform", name="Skeleton")
        root_jnt = Node.create("joint", name="BB_M_0_Root", parent=skeleton_grp.name)

        manip_world = Manip("M_0_World")
        manip_world.build(scale=20.0, shape="rounded_square")
        manip_world.snap(root_jnt)
        manip_world.set_parent(module_root)

        manip_root = Manip("M_0_Root")
        manip_root.build(scale=17.0)
        manip_root.snap(root_jnt)
        manip_root.set_parent(manip_world)
        
        cmds.parentConstraint(manip_root.name, root_jnt.name)