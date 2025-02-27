from __future__ import annotations
from contextlib import contextmanager
import logging
import time
from typing import Optional

import numpy as np
from scipy.optimize import nnls

import maya.cmds as cmds
from maya.api import OpenMaya as om, OpenMayaAnim as oma


log = logging.getLogger("SSDR")
log.setLevel(logging.DEBUG)


# ----------------------------------------------------------------
# Utils
# ----------------------------------------------------------------

_msl = om.MSelectionList()
kIdentityMatrix = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0]).reshape(4, 4)


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
        
    def _update_weights(self):
        weights = self._fn.getWeights(self._output_shape.path, self._output_shape.get_components(), self.influence_ids)
        self._weights = np.array(weights).reshape(self._output_shape.num_vertices, self.influence_count)
    
    def set_weights(self, weights: np.array | om.MDoubleArray, vertex_ids: Optional[np.array | list | tuple] = None,
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
                    nodes = harvest(child, om.MFn.kSkinClusterFilter)
                    if len(nodes) > 0:
                        break
        else:
            nodes = harvest(obj, om.MFn.kSkinClusterFilter)

        count = len(nodes)
        if count == 0:
            return
        elif count == 1:
            return Skin(nodes[0])
        else:
            raise Exception("Multiple node found.")
    
    @property
    def weights(self) -> np.array:
        return self._weights
    
    @property
    def max_influences(self) -> int:
        return cmds.getAttr(f"{self._fn.name()}.maxInfluences")

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
    
    def get_joint_matrices(self) -> np.array:
        matrices = []
        for i in range(self.influence_count):
            marix = self._influences_path[i].inclusiveMatrix()
            matrices.append(np.array(marix).reshape(4, 4))
        
        return np.array(matrices)


@contextmanager
def GiveTime(msg: str):
    current_time = time.time()
    try:
        yield
    finally:
        log.info(f"{msg}: {time.time() - current_time}")


@contextmanager
def KeepTime():
    current_time = cmds.currentTime(query=True)
    try:
        yield
    finally:
        cmds.currentTime(current_time)


@contextmanager
def SuspendRefresh():
    cmds.refresh(suspend=True)
    try:
        yield
    finally:
        cmds.refresh(suspend=False)


def harvest(mo, mfn_type: om.MFn) -> om.MObjectArray:
    iterator = om.MItDependencyGraph(mo, mfn_type,
                                     om.MItDependencyGraph.kUpstream,
                                     om.MItDependencyGraph.kDepthFirst,
                                     om.MItDependencyGraph.kNodeLevel)
    output = om.MObjectArray()
    while iterator.isDone() is False:
        output.append(iterator.currentNode())
        iterator.next()

    return output


def get_object(node: str) -> om.MObject:
    try:
        _msl.clear()
        _msl.add(node)
        return _msl.getDependNode(0)
    except RuntimeError:
        raise RuntimeError(f"Node {node} does not exist !")


def get_path(node: str | om.MObject) -> om.MDagPath:
    if isinstance(node, om.MObject):
        if not node.hasFn(om.MFn.kDagNode):
            raise RuntimeError(f"Node {om.MFnDependencyNode(node).name()} is not a dagNode !")
        return om.MDagPath.getAPathTo(node)
    try:
        _msl.clear()
        _msl.add(node)
        return _msl.getDagPath(0)
    except RuntimeError:
        raise RuntimeError(f"Node {node} does not exist !")


def name(obj: str | om.MObject | om.MPlug, full: bool = True, namespace: bool = True) -> str:
    if isinstance(obj, om.MDagPath):
        name_str = obj.fullPathName()
    elif isinstance(obj, om.MPlug):
        node_name = name(obj.node())
        attr_name = om.MFnAttribute(obj.attribute()).name()
        name_str = f"{node_name}.{attr_name}"
    elif isinstance(obj, om.MObject):
        if not obj.hasFn(om.MFn.kDagNode):
            name_str = om.MFnDependencyNode(obj).name()
        else:
            name_str = om.MFnDagNode(obj).fullPathName()
    else:
        raise TypeError(f"Argument must be a MObject not {type(obj)}")
    if not full:
        name_str = name_str.split('|')[-1]
    if not namespace:
        name_str = name_str.split(':')[-1]
    return name_str


def get_points(obj: str | om.MDagPath | om.MObject):
    if not isinstance(obj, om.MDagPath):
        obj = get_path(obj)
    mfn = om.MFnMesh(obj)
    points = mfn.getPoints(om.MSpace.kObject)
    return points


def solve_nnls(A, b):
    x, _ = nnls(A, b)
    x[x < 1e-4] = 0
    s = np.sum(x)
    if s > 1e-8:
        x /= s

    return x


# ----------------------------------------------------------------
# API Utils
# ----------------------------------------------------------------

class SSDR:

    def __init__(self, src_mesh: str, dst_mesh: str, start_frame: Optional[int] = None, end_frame: Optional[int] = None,
                 max_itererations: int = 30, tolerence: float = 1e-4, reinit_threshold: float = 1e-6):
        self._src_mesh = src_mesh
        self._dst_mesh = dst_mesh
        self._dst_skin = Skin.find(self._dst_mesh)
        if not self._dst_skin:
            raise RuntimeError("No skin cluster found on destination mesh.")

        self._start_frame = start_frame
        self._end_frame = end_frame
        self._rest_pose = []
        self._poses = []
        self._num_pose = 0
        self._num_vertices = 0
        self._num_bones = 0
        self._max_influences = 0
        self._max_itererations = max_itererations
        self._tolerence = tolerence
        self.reinit_threshold = reinit_threshold
        self._weights = None
        self._transforms = None
        self._pose_transforms = None
        self._rest_transforms = None

        self._init_data()
    
    def _init_data(self):
        self._get_time()
        self._get_data()
    
    def _get_time(self):
        if self._start_frame is None:
            self._start_frame = cmds.playbackOptions(query=True, min=True)
        if self._end_frame is None:
            self._end_frame = cmds.playbackOptions(query=True, max=True)
        self._num_pose = int(self._end_frame - self._start_frame)

    def _get_data(self):
        cmds.currentTime(self._start_frame)
        joint_matrices = np.array(self._dst_skin.get_joint_matrices())

        poses = []
        with SuspendRefresh():
            with KeepTime():
                for t in range(0, self._num_pose):
                    cmds.currentTime(t)
                    poses.append(get_points(self._src_mesh))

        self._poses = np.array(poses)
        self._rest_pose = self._poses[0].copy()
        self._num_vertices = len(self._rest_pose)
        self._num_bones = self._dst_skin.influence_count
        self._max_influences = self._dst_skin.max_influences
        self._transforms = np.repeat(np.expand_dims(joint_matrices, axis=0), self._num_pose, axis=0)
        self._rest_transforms = [np.linalg.inv(x) for x in joint_matrices.copy()]
        self._weights = np.zeros((self._num_vertices, self._num_bones))

    def update_weights(self):
        for v in range(self._num_vertices):
            A = []
            for t in range(self._num_pose):
                point = self._rest_pose[v]
                joint_transformations = [self._rest_transforms[i] @ j for i, j in enumerate(self._transforms[t])]
                A.append(np.array([point @ joint for joint in joint_transformations]).T)

            A = np.vstack(A)
            b = np.hstack(self._poses[:, v])
            weights = solve_nnls(A, b)
            # ToDo: Clamp with max influences
            self._weights[v] = weights

    def update_bones(self):
        for t in range(self._num_pose):
            for j in range(self._num_bones):
                weights = self._weights[:, j]
                if np.sum(weights**2) < self.reinit_threshold:
                    self.reinitialize_bone(t, j)
                    continue
                weights_sum = np.sum(weights)
                p_centroid = np.sum(weights[:, None] * self._rest_pose, axis=0) / weights_sum
                v_centroid = np.sum(weights[:, None] * self._poses[t], axis=0) / weights_sum
                p_centered = self._rest_pose - p_centroid
                v_centered = self._poses[t] - v_centroid
                C = (weights[:, None] * p_centered).T @ v_centered
                U, S, Vt = np.linalg.svd(C)
                R_opt = Vt.T @ U.T
                if np.linalg.det(R_opt) < 0:
                    Vt[-1, :] *= -1
                    R_opt = Vt.T @ U.T
                T_opt = v_centroid - R_opt @ p_centroid

                transformation_matrix = np.eye(4)
                transformation_matrix[:3, :3] = R_opt[:3, :3]
                transformation_matrix[3, :3] = T_opt[:3]
                self._transforms[t, j] = transformation_matrix

    def reinitialize_bone(self, t, j, neighbor_count=20):
        self._transforms[t, j] = kIdentityMatrix.copy()

    def compute_error(self):
        err = 0.0
        for t in range(self._num_pose):
            for v in range(self._num_vertices):
                # Solve
                pred = np.zeros(3)
                for j in range(self._num_bones):
                    # Transform matrix
                    matrix = self._transforms[t, j].reshape(4, 4)
                    rotation = matrix[:3, :3]
                    translation = matrix[:, 3][:3]
                    pred += self._weights[v, j] * (rotation @ self._rest_pose[v][:3] + translation)
                err += np.linalg.norm(self._poses[t][v][:3] - pred)**2

        return err

    def run(self):
        prev_err = np.inf
        for it in range(self._max_itererations):
            log.debug(f"Itération {it}...")
            log.debug("Compute Weights...")
            self.update_weights()
            log.debug("Compute Transforms...")
            self.update_bones()
            log.debug("Compute Errors...")
            err = self.compute_error()
            log.debug(f"Reconstruction Error : {err:.6f}")
            if abs(prev_err - err) / (prev_err + 1e-8) < self._tolerence:
                break
            prev_err = err
        log.debug("SDDR completed.")
    
    def set_skin_weights(self):
        with GiveTime("Set skin weights"):
            self._dst_skin.set_weights(self._weights.reshape(self._num_vertices * self._num_bones))

    def set_joint_transforms(self):
        with GiveTime("Set joint transforms"):
            with KeepTime():
                for t in range(self._num_pose):
                    cmds.currentTime(t)
                    for j in range(self._num_bones):
                        jnt = self._dst_skin._influences_path[j].fullPathName()
                        cmds.xform(jnt, matrix=self._transforms[t, j].reshape(16), worldSpace=True)
                        cmds.setKeyframe(jnt)
    
    def apply(self):
        self.set_skin_weights()
        self.set_joint_transforms()


# ----------------------------------------------------------------
# Excecute
# ----------------------------------------------------------------

def main(src_node: str, dst_node: str):
    ssdr = SSDR(src_node, dst_node)
    with GiveTime("SSDR Take"):
        ssdr.run()
    with GiveTime("Apply SSDR Take"):
        ssdr.apply()


"""
import imp
from HodoRig.RnD import ssdr
imp.reload(ssdr)

ssdr.main("truthShape", "approximationShape")
"""