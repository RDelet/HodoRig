from __future__ import annotations
from typing import Optional, Tuple
from time import time

import numpy as np

from maya.api import OpenMaya as om, OpenMayaAnim as oma

from .constants import SmoothMethod
from ...Helpers.utils import get_object, get_path
from ...Core.math import barycentric_coordinate


class Node:

    def __init__(self, obj: str | om.MObject):
        if isinstance(obj, str):
            obj = get_object(obj)
        self._handle = om.MObjectHandle(obj)
        self._fn = om.MFnDependencyNode(obj)
    
    @property
    def object(self) -> om.MObject:
        return self._handle.object()


class Mesh(Node):

    def __init__(self, obj: str | om.MObject):
        super().__init__(obj)
        if not self.object.hasFn(om.MFn.kMesh):
            raise TypeError(f"Obj must be a shape not {self.object.apiTypeStr}")
        self._fn = om.MFnMesh(self.object)
    
    def update_surface(self):
        self._fn.updateSurface()
    
    @property
    def path(self) -> om.MDagPath:
        return get_path(self.object)
    
    def get_components(self, vertex_ids: Optional[np.array] = None) -> om.MObject:
        mfn = om.MFnSingleIndexedComponent()
        obj = mfn.create(om.MFn.kMeshVertComponent)
        if vertex_ids is not None:
            mfn.addElements(vertex_ids)
        else:
            mfn.addElements(list(range(self._fn.numVertices)))

        return obj
    
    @property
    def num_vertices(self) -> int:
        return self._fn.numVertices
    
    def get_vertex_positions(self, world: bool = False) -> np.array:
        fn = self._fn if not world else om.MFnMesh(get_path(self.object))
        points = fn.getPoints(om.MSpace.kObject if not world else om.MSpace.kWorld)

        return np.array(om.MVectorArray(points))

    def get_triangles(self) -> Tuple[om.MIntArray, om.MIntArray]:
        return self._fn.getTriangles()
    
    def get_neightboor_vertices(self, vertex_ids: np.array) -> np.array:
        mit = om.MItMeshVertex(self.object)
        neightboors = []
        if not vertex_ids.shape[0]:
            while not mit.isDone():
                neightboors.append(mit.getConnectedVertices())
                mit.next()
        else:
            for vertex_id in vertex_ids:
                mit.setIndex(int(vertex_id))
                neightboors.append(mit.getConnectedVertices())
        
        """
        # Get vertexfrom adjacent polygons
        mit.setIndex(139)
        connected_vertices = []
        for face_id in mit.getConnectedFaces():
            connected_vertices.extend(mfn.getPolygonVertices(face_id))
        connected_vertices = sorted(list(set(connected_vertices)))
        """
        
        return np.array(neightboors)
    
    def create_normalized_adjacency(self, vertex_ids: Optional[np.array | list | tuple] = None) -> np.array:
        neighbors = self.get_neightboor_vertices(vertex_ids=vertex_ids)
        n_vertices = len(neighbors)
        A = np.zeros((n_vertices, self.num_vertices), dtype=float)
        for i in range(n_vertices):
            if len(neighbors[i]) == 0:
                A[i, i] = 1.0
            else:
                weight = 1.0 / len(neighbors[i])
                for j in neighbors[i]:
                    A[i, j] = weight
        
        return A

    def get_selected_vertices(self):
        selection = om.MGlobal.getActiveSelectionList()
        if selection.length() == 0:
            return []

        vertex_ids = []
        for i in range(selection.length()):
            dag_path, component = selection.getComponent(i)
            if dag_path.node() != self.object:
                continue
            if component.apiType() == om.MFn.kMeshVertComponent:
                iter_comp = om.MItMeshVertex(dag_path, component)
                while not iter_comp.isDone():
                    vertex_ids.append(iter_comp.index())
                    iter_comp.next()

        return vertex_ids


class Skin(Node):

    def __init__(self, skin_obj: str | om.MObject):
        if isinstance(skin_obj, str):
            skin_obj = get_object(skin_obj)

        self._fn = oma.MFnSkinCluster(skin_obj)
        self._influences_path = self._fn.influenceObjects()
        self._weights = None
        self._output_shape = Mesh(self._get_output_shape())  # ToDo: Factory for other shape
        self._input_shape = Mesh(self._get_input_shape())

        self._update_weights()
    
    @property
    def output_shape(self) -> Mesh:
        return self._output_shape
        
    def _update_weights(self):
        weights = self._fn.getWeights(self._output_shape.path, self._output_shape.get_components(), self.influence_ids)
        self._weights = np.array(weights).reshape(self._output_shape.num_vertices, self.influence_count)
    
    def _set_weights(self, weights: np.array | om.MDoubleArray, vertex_ids: Optional[np.array | list | tuple] = None,
                     normalize: bool = False, return_old: bool = True) -> om.MDoubleArray:
        if not isinstance(weights, om.MDoubleArray):
            weights = om.MDoubleArray(weights)
        return self._fn.setWeights(self._output_shape.path, self._output_shape.get_components(vertex_ids),
                                   self.influence_ids, weights, normalize=normalize, returnOldWeights=return_old)
    
    def _get_output_shape(self) -> om.MObject:
        shapes = self._fn.getOutputGeometry()
        if len(shapes) == 0:
            raise RuntimeError(f"No output geometry found on {self.object}!")
        return shapes[0]
    
    def _get_input_shape(self) -> om.MObject:
        shapes = self._fn.getInputGeometry()
        if len(shapes) == 0:
            raise RuntimeError(f"No input geometry found on {self.object}!")
        return shapes[0]

    @classmethod
    def find(cls, obj: str | om.MObject) -> Optional[Skin]:
        if isinstance(obj, str):
            obj = get_object(obj)
        if obj.hasFn(om.MFn.kDagNode) is False:
            raise Exception("Argument must be a DagNode.")

        nodes = om.MObjectArray()
        if obj.hasFn(om.MFn.kTransform):
            mfn = om.MFnTransform(obj)
            for i in range(mfn.childCount()):
                child = mfn.child(i)
                if child.hasFn(om.MFn.kShape):
                    nodes = cls._harvest(child, om.MFn.kSkinClusterFilter)
                    if len(nodes) > 0:
                        break
        else:
            nodes = cls._harvest(obj, om.MFn.kSkinClusterFilter)

        count = len(nodes)
        if count == 0:
            return
        elif count == 1:
            return Skin(nodes[0])
        else:
            raise Exception("Multiple node found.")
    
    @staticmethod
    def _harvest(mo, mfn_type: om.MFn) -> om.MObjectArray:
        iterator = om.MItDependencyGraph(mo, mfn_type,
                                        om.MItDependencyGraph.kUpstream,
                                        om.MItDependencyGraph.kDepthFirst,
                                        om.MItDependencyGraph.kNodeLevel)
        output = om.MObjectArray()
        while iterator.isDone() is False:
            output.append(iterator.currentNode())
            iterator.next()

        return output
    
    @property
    def influence_count(self) -> int:
        return len(self._influences_path)
    
    @property
    def influence_ids(self) -> om.MIntArray:
        # ToDo: Use api to get real ids
        return om.MIntArray(list(range(len(self._influences_path))))

    @property
    def influence_names(self) -> np.array:
        return [x.fullPathName() for x in self._influences_path]
    
    @staticmethod
    def normalize_weights(weights: np.array | om.MDoubleArray) -> np.array:
        if isinstance(weights, om.MDoubleArray):
            pass

        row_sums = weights.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1.0

        return weights / row_sums

    def _get_mask(self, vertex_ids: Optional[np.array] = None) -> np.array:
        if vertex_ids is None:
            vertex_ids = self._output_shape.get_selected_vertices() or list(range(self._output_shape.num_vertices))
        mask = np.zeros(self._output_shape.num_vertices, dtype=bool)
        mask[vertex_ids] = True

        return mask

    def smooth(self, smooth_method: SmoothMethod, relax_factor: float = 1.0,
               iterations: int = 10, dt: float = 0.1, epsilon: float = 1e-6,
               vertex_ids: Optional[np.array] = None):
        mask = self._get_mask(vertex_ids)
        if smooth_method == SmoothMethod.RELAX:
            self._relax(mask, relax_factor=relax_factor)
        elif smooth_method == SmoothMethod.DISTANCE_WEIGHTED:
            self._distance_weighted(mask, relax_factor=relax_factor, epsilon=epsilon)
        elif smooth_method == SmoothMethod.HEAT_DIFFUSION:
            self._heat_diffusion(mask, dt=dt, iterations=iterations)
        elif smooth_method == SmoothMethod.BARYCENTRIC:
            self._barycentric(mask, relax_factor=relax_factor)
        else:
            raise RuntimeError("Invalid smooth solver given !")
    
    def _relax(self, mask: np.array, relax_factor: float = 1.0):
        self._update_weights()
        indices = np.nonzero(mask)[0]

        A = self._output_shape.create_normalized_adjacency(indices)
        new_weights = (1 - relax_factor) * self._weights[indices] + relax_factor * (A @ self._weights)
        new_weights = self.normalize_weights(new_weights).reshape(self.influence_count * indices.shape[0])

        self._set_weights(new_weights, vertex_ids=indices)
    
    def _distance_weighted(self, mask: np.array, relax_factor: float = 1.0, epsilon: float = 1e-6):
        self._update_weights()
        indices = np.nonzero(mask)[0]
        positions = self._input_shape.get_vertex_positions()
        neighbors = self._input_shape.get_neightboor_vertices(indices)
        n_sel = len(indices)

        A = np.zeros((n_sel, self._input_shape.num_vertices), dtype=float)
        for i, vid in enumerate(indices):
            nbrs = neighbors[i]
            if len(nbrs) == 0:
                A[i, vid] = 1.0
            else:
                dists = np.array([np.linalg.norm(positions[vid] - positions[j]) for j in nbrs])
                inv_dists = 1.0 / (dists + epsilon)
                inv_dists /= inv_dists.sum()
                for k, j in enumerate(nbrs):
                    A[i, j] = inv_dists[k]
        new_sel = (1 - relax_factor) * self._weights[indices] + relax_factor * (A @ self._weights)
        new_sel = self.normalize_weights(new_sel).reshape(len(indices) * self.influence_count)

        self._set_weights(new_sel, vertex_ids=indices)
   
    def _heat_diffusion(self, mask: np.array, dt: float = 0.1, iterations: int = 10):
        self._update_weights()
        indices = np.nonzero(mask)[0]

        A = self._output_shape.create_normalized_adjacency(indices)
        new_weights = self._weights[indices].copy()
        for _ in range(iterations):
            new_weights = self.normalize_weights(new_weights + dt * ((A @ self._weights) - new_weights))
        weights_to_set = new_weights.reshape(len(indices) * self.influence_count)

        self._set_weights(weights_to_set, vertex_ids=indices)
    
    def _barycentric(self, mask: np.array, relax_factor: float = 1.0):
        self._update_weights()
        indices = np.nonzero(mask)[0]
        positions = self._output_shape.get_vertex_positions()
        neighbors = self._output_shape.get_neightboor_vertices(indices)
        new_weights = self._weights.copy()

        for i, vtx_id in enumerate(indices):
            adjacent_vertices = neighbors[i]
            if len(adjacent_vertices) < 2:
                continue

            triangles = []
            center = positions[vtx_id]
            if len(adjacent_vertices) == 3:
                triangles.append([adjacent_vertices[0], adjacent_vertices[1], adjacent_vertices[2]])
            elif len(adjacent_vertices) == 4:  
                triangles.append([adjacent_vertices[0], adjacent_vertices[1], adjacent_vertices[2]])
                triangles.append([adjacent_vertices[2], adjacent_vertices[3], adjacent_vertices[0]])
            else:
                for i in range(1, len(adjacent_vertices) - 1):
                    triangles.append([adjacent_vertices[0], adjacent_vertices[i], adjacent_vertices[i + 1]])

            face_weights = np.zeros(self.influence_count)
            for tri in triangles:
                p0, p1, p2 = positions[tri[0]], positions[tri[1]], positions[tri[2]]
                la, lb, lc = barycentric_coordinate(center, p0, p1, p2)
                tri_weights = la * self._weights[tri[0]] + lb * self._weights[tri[1]] + lc * self._weights[tri[2]]
                face_weights += tri_weights
            face_weights /= len(triangles)

            new_weights[vtx_id] = (1 - relax_factor) * self._weights[vtx_id] + relax_factor * face_weights

        new_weights = self.normalize_weights(new_weights)
        self._set_weights(new_weights.reshape(self.influence_count * self._output_shape.num_vertices), vertex_ids=indices)
    

def main():
    skin = Skin("skinCluster2")
    f = time()
    # skin.smooth(SmoothMethod.RELAX, relax_factor=1.0)
    skin.smooth(SmoothMethod.DISTANCE_WEIGHTED, relax_factor=1.0, epsilon=1e-6)
    # skin.smooth(SmoothMethod.HEAT_DIFFUSION, dt=1.0, iterations=15)
    # skin.smooth(SmoothMethod.BARYCENTRIC, relax_factor=1.0,)
    print(f"HODOR: {time() - f}")

