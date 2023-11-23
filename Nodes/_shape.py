from __future__ import annotations
import os

from maya import cmds
from maya.api import OpenMaya

from HodoRig.Core import constants, file, point
from HodoRig.Core.logger import log
from HodoRig.Nodes._dagNode import _DAGNode
from HodoRig.Nodes.node import Node


class _Shape(_DAGNode):

    kApiType = OpenMaya.MFn.kShape

    def __init__(self, node: str | OpenMaya.MObject):
        super().__init__(node)

    def points(self, *args, **kwargs) -> OpenMaya.MPointArray:
        raise NotImplementedError(f"{self.__class__.__name__}.points need to be reimplemented !")
    
    def set_points(self, *args, **kwargs):
        raise NotImplementedError(f"{self.__class__.__name__}.set_points need to be reimplemented !")

    def components(self) -> OpenMaya.MObject:
        raise NotImplementedError(f"{self.__class__.__name__}.components need to be reimplemented !")

    def to_dict(self, normalize: bool = True) -> dict:
        raise NotImplementedError(f"{self.__class__.__name__}.to_dic need to be reimplemented !")

    @classmethod
    def from_dict(cls, data: dict, parent: str | OpenMaya.MObject,
                  shape_dir: int = None, scale: float = None):
        raise NotImplementedError(f"{cls.__name__}.from_dict need to be reimplemented !")
    
    def update(self):
        raise NotImplementedError(f"{self.__class__.__name__}.update need to be reimplemented !")
    
    @classmethod
    def load(cls, file_name: str, parent: str | OpenMaya.MObject,
             shape_dir: int = None, scale: float = None):
        file_path = os.path.join(constants.kShapeDir, f"{file_name}.{constants.kShapeExtension}")
        data = file.read_json(file_path)
        log.info(f"File read: {file_path}")
        return cls.from_dict(data, parent, shape_dir=shape_dir, scale=scale)

    def dump(self, file_name: str, normalize: bool = True):
        output_path = os.path.join(constants.kShapeDir, f"{file_name}.{constants.kShapeExtension}")
        file.dump_json(self.to_dict(normalize=normalize), output_path)
        log.info(f"File write: {output_path}")

    def scale(self, factor: float, normalize: bool = False):
        points = self.points(normalize=normalize)
        point.scale(points, factor)
        self.set_points(points)
        self.update()
