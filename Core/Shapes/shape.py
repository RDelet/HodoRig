from typing import Union

from maya import cmds
from maya.api import OpenMaya

from HodoRig.Core import constants, utils
from HodoRig.Core.Shapes import mesh, curve, surface, point


shape_getter = {constants.kCurveApi: curve.shape_to_dict,
                constants.kCurve: curve.shape_to_dict,
                constants.kMeshApi: mesh.shape_to_dict,
                constants.kMesh: mesh.shape_to_dict,
                constants.kSurfaceApi: surface.shape_to_dict,
                constants.kSurface: surface.shape_to_dict}


shape_builder = {constants.kCurveApi: curve.dict_to_shape,
                 constants.kCurve: curve.dict_to_shape,
                 constants.kMeshApi: mesh.dict_to_shape,
                 constants.kMesh: mesh.dict_to_shape,
                 constants.kSurfaceApi: surface.dict_to_shape,
                 constants.kSurface: surface.dict_to_shape}


_modules = {constants.kCurveApi: curve,
           constants.kCurve: curve,
           constants.kMeshApi: mesh,
           constants.kMesh: curve,
           constants.kSurfaceApi: surface,
           constants.kSurface: curve,}


class Shape:

    def __init__(self, node: Union[str, OpenMaya.MObject]):
        self._node = utils.check_object(node)
        if not self._node.hasFn(OpenMaya.MFn.kShape):
            raise RuntimeError("Node must be a shape !")
    
    @property
    def name(self) -> str:
        return utils.name(self._node)
    
    @property
    def short_name(self) -> str:
        return utils.name(self._node, False, False)
    
    @property
    def api_type(self) -> int:
        return self._node.apiType()
    
    @property
    def type(self) -> str:
        return cmds.nodeType(self.name)

    def get_points(self, normalize: bool = False) -> OpenMaya.MPointArray:
        shape_type = self.type
        if shape_type not in _modules:
            raise RuntimeError(f"Node type {shape_type} not valid shape !")
        return _modules[shape_type].get_points(self._node, normalize=normalize)
    
    def set_points(self, points):
        shape_type = self.type
        if shape_type not in _modules:
            raise RuntimeError(f"Node type {shape_type} not valid shape !")
        _modules[shape_type].set_points(self._node, points)
    
    def scale(self, factor: float, normalize: bool = False):
        points = self.get_points(normalize=normalize)
        point.scale(points, factor)
        self.set_points(points)
        self.update()
    
    def update(self):
        shape_type = self.type
        if shape_type not in _modules:
            raise RuntimeError(f"Node type {shape_type} not valid shape !")
        _modules[shape_type].update(self._node)
        

