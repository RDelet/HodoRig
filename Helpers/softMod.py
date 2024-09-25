from maya.api import OpenMaya, OpenMayaAnim

from ..Core import mesh
from ..Helpers import utils
from ..Core.component import SoftVertex
from ..Helpers.deformer import Deformer


class SoftMod(Deformer):

    def get_soft_mod_weights(self):

        path = utils.get_path(self._shape)
        component = mesh.get_vertex_component(self._shape)
        weights = OpenMaya.MFloatArray()
        mfn = OpenMayaAnim.MFnWeightGeometryFilter(self._object)
        mfn.getWeights(path, component, weights)

        node = path.fullPathName()
        mfn = OpenMaya.MFnSingleIndexedComponent(component)
        soft_vertices = []
        for i in range(mfn.elementCount()):
            if weights[i] < 1e-4:
                continue
            soft_vertices.append(SoftVertex(node, mfn.element(i), weights[i]))

        return soft_vertices
