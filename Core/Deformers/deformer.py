import json
from typing import Union

from maya.api import OpenMaya, OpenMayaAnim

from HodoRig.Core import utils
from HodoRig.Core.logger import log
from HodoRig.Core.jsonEncoder import JsonEncoder
from HodoRig.Core.Shapes import mesh


class Deformer(object):

    _kValidShape = [OpenMaya.MFn.kMesh]

    def __init__(self, node: Union[str, OpenMaya.MObject] = None):
        self._object = None
        if node:
            self._get_data(node)

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name: {self.name})"

    def _clear(self):
        pass

    def _get_data(self, node: Union[str, OpenMaya.MObject]):
        """!@Brief Get deformer data."""

        if isinstance(node, str):
            node = utils.get_object(node)

        if not self.is_deformer(node):
            raise RuntimeError(f"Node {utils.name(node)} is not a deformer")

        self._clear()
        self._object = node

        shapes = self.outputs_geometry()
        if len(shapes) == 0:
            raise RuntimeError('No output shape found for "{0}" !'.format(self.name))
        
        if not self.valid_shape(shapes[0]):
            raise RuntimeError("No valid shape given !")

        self._shape = shapes[0]
        if self._shape.hasFn(OpenMaya.MFn.kMesh):
            self._shape_data = mesh.shape_to_dict(self._shape)
        else:
            raise TypeError('Only mesh is implemented !')

    @property
    def name(self) -> str:
        return utils.name(self._object) if self._object else ''

    @property
    def object(self) -> OpenMaya.MObject:
        return self._object

    def outputs_geometry(self) -> OpenMaya.MObjectArray:
        """!@Brief Get all output deformer shapes."""
        output_geom = OpenMaya.MObjectArray()
        if self._object:
            mfn = OpenMayaAnim.MFnGeometryFilter(self._object)
            output_geom = mfn.getOutputGeometry()

        return output_geom

    def inputs_geometry(self) -> OpenMaya.MObjectArray:
        """!@Brief Get all orig deformer shape."""
        input_geom = OpenMaya.MObjectArray()
        if self._object:
            mfn = OpenMayaAnim.MFnGeometryFilter(self._object)
            input_geom = mfn.getInputGeometry()

        return input_geom

    @classmethod
    def is_deformer(cls, node: Union[str, OpenMaya.MObject]) -> bool:
        if isinstance(node, str):
            node = utils.get_object(node)
        return node.hasFn(OpenMaya.MFn.kGeometryFilt)

    @classmethod
    def valid_shape(cls, node: Union[str, OpenMaya.MObject]) -> bool:
        if isinstance(node, str):
            node = utils.get_object(node)

        return node.apiType() in cls._kValidShape
    
    @classmethod
    def _find(cls, node: Union[str, OpenMaya.MObject, OpenMaya.MDagPath], mfn_type: int) -> OpenMaya.MObject:
        """!@Brief Get skinCluster from shape object."""

        def __harvest(mo) -> OpenMaya.MObjectArray:
            mit_dg = OpenMaya.MItDependencyGraph(mo, mfn_type,
                                                 OpenMaya.MItDependencyGraph.kUpstream,
                                                 OpenMaya.MItDependencyGraph.kDepthFirst,
                                                 OpenMaya.MItDependencyGraph.kNodeLevel,)
            output = OpenMaya.MObjectArray()
            while mit_dg.isDone() is False:
                output.append(mit_dg.currentNode())
                mit_dg.next()

            return output

        if isinstance(node, str):
            node = utils.get_object(node)
        if node.hasFn(OpenMaya.MFn.kDagNode) is False:
            raise Exception("Argument must be a DagNode.")

        nodes = OpenMaya.MObjectArray()
        if node.hasFn(OpenMaya.MFn.kTransform):
            mfn = OpenMaya.MFnTransform(node)
            for i in range(mfn.childCount()):
                child = mfn.child(i)
                if child.hasFn(OpenMaya.MFn.kShape):
                    nodes = __harvest(child)
                    if len(nodes) > 0:
                        break
        else:
            nodes = __harvest(node)

        count = len(nodes)
        if count == 0:
            return
        elif count == 1:
            return nodes[0]
        else:
            raise Exception("Multiple node found.")
    
    def bind(self):
        raise NotImplementedError(f"{self.__class__.__name__}.bind need to be reimplemented !")
    
    def save(self, output_path: str):
        if self.is_empty():
            raise Exception(f"Data of {self.__class__.__name__} instance is empty !")
        
        data_str = json.dumps(self.to_dict(), indent=4, cls=JsonEncoder)
        with open(output_path, "w") as stream:
            stream.write(data_str)
        
        log.debug(f"{self.__class__.__name__} file write -> {output_path}")
