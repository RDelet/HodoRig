from typing import Union

from maya.api import OpenMaya

from HodoRig.Core import curve, constants, mesh, surface, utils
from HodoRig.Core.logger import log
from HodoRig.Builders.builder import Builder


shape_getter = {OpenMaya.MFn.kNurbsCurve: curve.shape_to_dict,
                OpenMaya.MFn.kMesh: mesh.shape_to_dict,
                OpenMaya.MFn.kNurbsSurface: surface.shape_to_dict}

shape_builder = {curve.kNodeType: curve.dict_to_shape,
                 mesh.kNodeType: mesh.dict_to_shape,
                 surface.kNodeType: surface.dict_to_shape}


class Shape(Builder):

    kFiledirectory = constants.kShapeDir
    kFileExtension = constants.kShapeExtension

    def __init__(self, parent: Union[str, OpenMaya.MObject]):
        super().__init__()

        self._parent = utils.check_object(parent)

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
        if api_type not in shape_getter:
            valid_type = "\n\t-NurbsCurve\n\t-NurbsSurface\n\t-Mesh"
            raise TypeError(f"Invalid shape type given. Accepted type or {valid_type}")

        return shape_getter[api_type](node, normalize=normalize)

    def _pre_build(self, *args, **kwargs):
        log.debug(f"{self.__class__.__name__} pre build: {utils.name(self._parent)} !")

    def _build(self, shape_dir: int = None, scale: float = None):
        log.debug(f"{self.__class__.__name__} post build: {utils.name(self._parent)} !")

        shapes = OpenMaya.MObjectArray()
        for shape_data in self._data:

            shape_type = shape_data[constants.kType]
            if shape_type not in shape_builder:
                valid_type = "\n\t-NurbsCurve\n\t-NurbsSurface\n\t-Mesh"
                raise TypeError(f"Invalid shape type. Accepted type or {valid_type}")

            func = shape_builder[shape_type]
            shape = func(shape_data, self._parent, shape_dir=shape_dir, scale=scale)
            shapes.append(shape)
            name = f"{utils.name(self._parent, False, False)}Shape1"
            utils.rename(shape, name, force=True)

        return shapes

    def _post_build(self, *args, **kwargs):
        log.debug(f"{self.__class__.__name__} post build: {utils.name(self._parent)} !")