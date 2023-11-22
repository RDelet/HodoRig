from typing import Union

from maya.api import OpenMaya

from HodoRig.Core import constants
from HodoRig.Core.logger import log
from HodoRig.Nodes.node import Node
from HodoRig.Builders.shape import Shape


class Manip(Node):

    def __init__(self, base_name: str, manip_type: str = constants.kFk):
        super().__init__()

        self._base_name = base_name
        self._type = manip_type
        self._shape = None
    
    
    def _pre_build(self, *args, **kwargs):
        log.debug(f"{self.__class__.__name__} {self._base_name} build: {self._base_name}.")

    def _build(self, shape: str = "circle", shape_dir: int = None, scale: float = None):
        log.debug(f"{self.__class__.__name__} build: {self._base_name}.")

        reset_name = f"RESET_{self._base_name}"
        manip_name = f"MANIP_{self._base_name}"

        self._parent = Node.create("transform", name=reset_name)
        manip = Node.create("transform", name=manip_name, parent=self._parent.name)
        self._object = manip.object

        self._shape = Shape.load(shape, manip.name)
        self._shape.parent = manip.object
        self._shape.build(shape_dir=shape_dir, scale=scale)
    
    def _post_build(self, *args, **kwargs):
        log.debug(f"{self.__class__.__name__} post build: {self._base_name}")
    
    def set_parent(self, parent: Union[str, OpenMaya.MObject, "Node"]):
        if isinstance(parent, (str, OpenMaya.MObject)):
            parent = Node(parent)
        self.parent.set_parent(parent)