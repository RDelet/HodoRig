from __future__ import annotations
import os

from maya.api import OpenMaya

from ..Helpers import point

from ..Core import constants, _factory, file
from ..Core.logger import log
from .dagNode import DAGNode


class Shape(DAGNode):

    kApiType = OpenMaya.MFn.kShape
    kShapes = {}

    def points(self, *args, **kwargs) -> OpenMaya.MPointArray:
        raise NotImplementedError(f"{self.__class__.__name__}.points need to be reimplemented !")
    
    def set_points(self, *args, **kwargs):
        raise NotImplementedError(f"{self.__class__.__name__}.set_points need to be reimplemented !")

    def components(self) -> OpenMaya.MObject:
        raise NotImplementedError(f"{self.__class__.__name__}.components need to be reimplemented !")

    def to_dict(self, normalize: bool = True) -> dict:
        raise NotImplementedError(f"{self.__class__.__name__}.to_dic need to be reimplemented !")

    @classmethod
    def from_dict(cls, data: dict | list, parent: str | OpenMaya.MObject,
                  shape_dir: int = None, scale: float = None) -> list:
        output = []

        if isinstance(data, dict):
            new_csl = cls._from_dict(data, parent, shape_dir=shape_dir, scale=scale)
            output.append(new_csl)
        if isinstance(data, (list, tuple)):
            for d in data:
                new_csl = cls._from_dict(d, parent, shape_dir=shape_dir, scale=scale)
                output.append(new_csl)

        return output
    
    @classmethod
    def _from_dict(cls, data: dict, parent: str | OpenMaya.MObject | DAGNode,
                    shape_dir: int = None, scale: float = None) -> Shape:
        if isinstance(parent, DAGNode):
            parent = parent.object

        shape_type = data.get(constants.kType)
        if not shape_type:
            raise RuntimeError("Invalid shape data !")

        if shape_type not in constants.kTypeToApi:
            raise RuntimeError(f"Shape type {shape_type} not implemented yet !")
        api_type = constants.kTypeToApi[shape_type]

        return _factory.registered()[api_type].from_dict(data, parent, shape_dir=shape_dir, scale=scale)
    
    def update(self):
        raise NotImplementedError(f"{self.__class__.__name__}.update need to be reimplemented !")
    
    @classmethod
    def load(cls, file_name: str, parent: str | OpenMaya.MObject | DAGNode,
             shape_dir: int = None, scale: float = None):
        file_path = os.path.join(constants.kShapeDir, f"{file_name}.{constants.kShapeExtension}")
        data = file.read_json(file_path)
        log.debug(f"File read: {file_path}")

        return cls.from_dict(data, parent, shape_dir=shape_dir, scale=scale)

    def dump(self, file_name: str, normalize: bool = True):
        output_path = os.path.join(constants.kShapeDir, f"{file_name}.{constants.kShapeExtension}")
        file.dump_json(self.to_dict(normalize=normalize), output_path)
        log.debug(f"File write: {output_path}")

    def scale(self, factor: float, normalize: bool = False):
        points = self.points(normalize=normalize, world=False)
        point.scale(points, factor)
        self.set_points(points, world=False)
        self.update()
