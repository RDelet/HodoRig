import os
from typing import Union

from maya.api import OpenMaya

from HodoRig.Core import constants, utils
from HodoRig.Core.Shapes import shape as shapeUtils
from HodoRig.Core.logger import log
from HodoRig.Builders.builder import Builder


class Shape(Builder):

    kFiledirectory = constants.kShapeDir
    kFileExtension = constants.kShapeExtension

    def __init__(self, parent: Union[str, OpenMaya.MObject] = None):
        super().__init__()

        self._parent = utils.check_object(parent) if parent else None
    
    @property
    def parent(self) -> OpenMaya.MObject:
        return self._parent
    
    @parent.setter
    def parent(self, value: OpenMaya.MObject):
        self._parent = utils.check_object(value)

    def get_from_node(self, node: Union[str, OpenMaya.MObject], normalize: bool = True):
        """!@Brief Get all shapes from node."""
        self._data = []
        if isinstance(node, str):
            node = utils.get_object(node)

        if node.hasFn(OpenMaya.MFn.kTransform) or node.hasFn(OpenMaya.MFn.kPluginTransformNode):
            mfn = OpenMaya.MFnDagNode(node)
            for i in range(mfn.childCount()):
                child = mfn.child(i)
                if child.hasFn(OpenMaya.MFn.kShape):
                    self._data.append(self.get_shape_data(child, normalize=normalize))
        elif node.hasFn(OpenMaya.MFn.kShape):
            self._data.append(self.get_shape_data(node, normalize=normalize))
        else:
            valid_type = "\n\t-Transform\n\t-NurbsCurve\n\t-NurbsSurface\n\t-Mesh"
            raise TypeError(f"Invalid shape type given. Accepted type {valid_type}")

    @classmethod
    def get_shape_data(cls, node: Union[str, OpenMaya.MObject], normalize: bool = True) -> dict:
        """!@Brief Get NurbsCurve shape data."""

        if isinstance(node, str):
            node = utils.get_object(node)

        api_type = node.apiType()
        if api_type not in shapeUtils.shape_getter:
            valid_type = "\n\t-NurbsCurve\n\t-NurbsSurface\n\t-Mesh"
            raise TypeError(f"Invalid shape type given. Accepted type or {valid_type}")

        return shapeUtils.shape_getter[api_type](node, normalize=normalize)

    def _pre_build(self, *args, **kwargs):
        log.debug(f"{self.__class__.__name__} pre build: {utils.name(self._parent)} !")

    def _build(self, shape_dir: int = None, scale: float = None):
        log.debug(f"{self.__class__.__name__} post build: {utils.name(self._parent)} !")

        shapes = OpenMaya.MObjectArray()
        for shape_data in self._data:

            shape_type = shape_data[constants.kType]
            if shape_type not in shapeUtils.shape_builder:
                valid_type = "\n\t-NurbsCurve\n\t-NurbsSurface\n\t-Mesh"
                raise TypeError(f"Invalid shape type. Accepted type or {valid_type}")

            func = shapeUtils.shape_builder[shape_type]
            shape = func(shape_data, self._parent, shape_dir=shape_dir, scale=scale)
            shapes.append(shape)
            name = f"{utils.name(self._parent, False, False)}Shape1"
            utils.rename(shape, name, force=True)

        return shapes

    def _post_build(self, *args, **kwargs):
        log.debug(f"{self.__class__.__name__} post build: {utils.name(self._parent)} !")
    
    @classmethod
    def load(cls, file_name: str, *args, **kwargs):
        file_path = os.path.join(constants.kShapeDir, f"{file_name}.{constants.kShapeExtension}")
        return super().load(file_path)

    def dump(self, file_name: str):
        output_path = os.path.join(constants.kShapeDir, f"{file_name}.{constants.kShapeExtension}")
        super().dump(output_path)
