from __future__ import annotations
from dataclasses import asdict, dataclass, field
from functools import partial
from typing import Tuple
from time import time
import traceback

import maya.cmds as cmds
import maya.api.OpenMaya as om
import numpy as np


_msl = om.MSelectionList()


# ----------------------------------------------------------------
# Utils
# ----------------------------------------------------------------

class Context:

    def __init__(self, *args, **kwargs):
        pass

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"class: {self.__class__.__name__}"

    def __enter__(self, *args, **kwargs):
        raise NotImplementedError('{0}.__enter__ need to be reimplemented !'.format(self.__class__.__name__))

    def __exit__(self, *args, **kwargs):
        raise NotImplementedError('{0}.__exit__ need to be reimplemented !'.format(self.__class__.__name__))


class TimerContext(Context):

    def __init__(self, print: bool = False):
        super().__init__()
        self._current_time = 0.0
        self._print = print

    def __enter__(self):
        if self._print:
            self._current_time = time()

    def __exit__(self, *args, **kwargs):
        if self._print:
            print(f"{self.__class__.__name__}: {time() - self._current_time}")


# ----------------------------------------------------------------
# API Utils
# ----------------------------------------------------------------

@dataclass
class UV(object):
    name: str
    u: list = field(default_factory=partial(list))
    v: list = field(default_factory=partial(list))

    @property
    def count(self) -> int:
        return len(self.u)
    
    def to_dict(self) -> dict:
        return asdict(self)


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


def is_orig(obj: str) -> bool:
    return cmds.getAttr(f"{obj}.intermediateObject") and obj.endswith("Orig")


def get_orig(obj: str | om.MObject | om.MDagPath) -> om.MDagPath:
    if not isinstance(obj, str):
        obj = name(obj)
    shapes = cmds.listRelatives(obj, shapes=True, fullPath=True, type="mesh") or []
    origs = [x for x in shapes if is_orig(x)]
    return get_path(origs[0]) if origs else None


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


def get_uvs(obj: str | om.MObject | om.MDagPath) -> dict:
    data = {}
    if not isinstance(obj, om.MDagPath):
        obj = get_path(obj)
    mfn = om.MFnMesh(obj)
    for uvSet in mfn.getUVSetNames():
        uv = UV(uvSet)
        data[uvSet] = uv
        u, v = mfn.getUVs(uvSet)
        uv.u = list(u)
        uv.v = list(v)
    return data


def set_uvs(obj, uv_data: list, uv_map: str = "map1"):
    if not isinstance(obj, om.MDagPath):
        obj = get_path(obj)
    mfn = om.MFnMesh(obj)
    u = om.MFloatArray(uv_data[0])
    v = om.MFloatArray(uv_data[1])
    mfn.setUVs(u, v, uv_map)
    cmds.refresh(force=True)


def get_points(obj: str | om.MDagPath | om.MObject):
    if not isinstance(obj, om.MDagPath):
        obj = get_path(obj)
    mfn = om.MFnMesh(obj)
    points = mfn.getPoints(om.MSpace.kObject)
    return points


def get_triangles(obj: str | om.MDagPath | om.MObject) -> np.array:
    if not isinstance(obj, om.MDagPath):
        obj = get_path(obj)
    mfn = om.MFnMesh(obj)
    _, t = mfn.getTriangles()
    return np.array([[t[i], t[i + 1], t[i + 2]] for i in range(0, len(t), 3)])


# ----------------------------------------------------------------
# API Utils
# ----------------------------------------------------------------

class UVDeformer:

    def __init__(self, node: str, uv_map: str = "map1"):
        self._cbs = []
        self._node = get_object(node)
        # Shape Data
        self._shape_path = get_path(self._node)
        self._shape_path.extendToShape(0)
        # Orig Data
        self._orig_path = get_orig(self._node)
        self._orig_points = np.array(om.MVectorArray(get_points(self._orig_path)))
        all_uvs = get_uvs(self._orig_path)
        if uv_map not in all_uvs:
            raise RuntimeError(f"UVMap {uv_map} does not exists on {self._orig_path.fullPathName()}")
        uvs = all_uvs[uv_map]
        self._orig_uv = np.array([uvs.u, uvs.v]).T
        # Other Data
        self._point_count = self._orig_points.shape[0]
        self._triangles = get_triangles(self._orig_path)
    
    def triangle_deformation_uv(self, triangle: np.array, deformed_point: np.array, uv: np.array) -> Tuple[np.array, float]:
        """!@Brief For a given triangle (subscripts in sort), calculate the contribution
                   local UV displacement in "pull-back" of the 3D deformation.
        """
        i, j, k = triangle
        D_xp = np.column_stack([deformed_point[j] - deformed_point[i], deformed_point[k] - deformed_point[i]])
        D_uv = np.column_stack([uv[j] - uv[i], uv[k] - uv[i]])
        
        try:
            inv_D_uv = np.linalg.inv(D_uv)
        except np.linalg.LinAlgError:
            return np.zeros((3, 2)), 0.0
        F = D_xp @ inv_D_uv
        
        uv_area = 0.5 * abs(np.linalg.det(D_uv))
        
        local_uv = np.zeros((3, 2))
        for local, v in enumerate([j, k]):
            d_x = deformed_point[v] - self._orig_points[v]
            v_uv = np.linalg.pinv(F) @ d_x
            local_uv[local + 1, :] = v_uv

        return local_uv, uv_area

    def _do(self):
        deformed_points = np.array(om.MVectorArray(get_points(self._shape_path)))
        base_uv = self._orig_uv.copy()
        uv_disp = np.zeros((self._point_count, 2))
        weights = np.zeros(self._point_count)
        
        for triangle in self._triangles:
            local_uv, uv_area = self.triangle_deformation_uv(triangle, deformed_points, base_uv)
            if uv_area == 0:
                continue
            i, j, k = triangle

            uv_disp[j] += local_uv[1] * uv_area
            weights[j] += uv_area
            uv_disp[k] += local_uv[2] * uv_area
            weights[k] += uv_area

        new_uv = base_uv.copy()
        for v in range(self._point_count):
            if weights[v] > 0:
                new_uv[v] += uv_disp[v] / weights[v]
        # Fix first vertex to avoid global deformation
        # ToDo: Give a set of vertices
        new_uv[0] = base_uv[0]

        set_uvs(self._orig_path, new_uv.T)

    def global_uv_minimization(self, deformed_points, fixed_index=0) -> np.array:
        """
        Résout globalement le problème de reconstruction UV.
        
        Parameters:
        - deformed_points : np.array de shape (n, 3) avec les positions déformées 3D.
        - fixed_index : l'indice du vertex à fixer (pour éliminer la liberté de translation).
        
        Returns:
        - new_uv : np.array de shape (n,2) avec les nouvelles UV.
        """
        orig_uv = self._orig_uv.copy()
        n = orig_uv.shape[0]
        T = self._triangles.shape[0]
        
        # Chaque triangle fournit 2 équations (pour les edges i->j et i->k)
        num_eq = 2 * T
        A = np.zeros((num_eq, n))
        b_u = np.zeros(num_eq)
        b_v = np.zeros(num_eq)
        
        eq = 0
        for t in range(T):
            tri = self._triangles[t]  # [i, j, k]
            local_uv, uv_area = self.triangle_deformation_uv(tri, deformed_points, orig_uv)
            # On peut choisir de pondérer chaque équation par sqrt(uv_area) pour plus de stabilité
            weight = np.sqrt(uv_area) if uv_area > 0 else 1.0
            
            i, j, k = tri
            # Equation pour l'edge i->j: U[j] - U[i] = local_uv[1]
            A[eq, j] = weight
            A[eq, i] = -weight
            b_u[eq] = weight * local_uv[1, 0]
            b_v[eq] = weight * local_uv[1, 1]
            eq += 1
            
            # Equation pour l'edge i->k: U[k] - U[i] = local_uv[2]
            A[eq, k] = weight
            A[eq, i] = -weight
            b_u[eq] = weight * local_uv[2, 0]
            b_v[eq] = weight * local_uv[2, 1]
            eq += 1

        # Ajouter une contrainte pour fixer le vertex fixed_index.
        A_fix = np.zeros((1, n))
        A_fix[0, fixed_index] = 1
        b_u_fix = np.array([orig_uv[fixed_index, 0]])
        b_v_fix = np.array([orig_uv[fixed_index, 1]])
        
        A_total = np.vstack([A, A_fix])
        b_u_total = np.concatenate([b_u, b_u_fix])
        b_v_total = np.concatenate([b_v, b_v_fix])
        
        # Ajouter un terme de régularisation pour améliorer la robustesse (lambda)
        lambda_reg = 1e-3
        LHS = A_total.T @ A_total + lambda_reg * np.eye(n)
        rhs_u = A_total.T @ b_u_total
        rhs_v = A_total.T @ b_v_total
        
        sol_u = np.linalg.solve(LHS, rhs_u)
        sol_v = np.linalg.solve(LHS, rhs_v)
        
        new_uv = np.stack([sol_u, sol_v], axis=-1)
        return new_uv

    def _do_global(self):
        deformed_points = np.array(om.MVectorArray(get_points(self._shape_path)))
        new_uv = self.global_uv_minimization(deformed_points)
        set_uvs(self._orig_path, new_uv.T)
 
    def do(self, *args, **kwargs):
        try:
            with TimerContext(print=False):
                self._do()
        except Exception as e:
            print(e)
            print(traceback.format_exc())
    
    def install_cbs(self):
        self.remove_cbs()
        for jnt in cmds.ls(type="joint", long=True):
            self._cbs.append(om.MDagMessage.addMatrixModifiedCallback(get_path(jnt), self.do))

    def remove_cbs(self):
        if self._cbs:
            om.MNodeMessage.removeCallbacks(self._cbs)
            self._cbs.clear()


# ----------------------------------------------------------------
# HODOR !!!
# ----------------------------------------------------------------

deformer = UVDeformer("pPlane1", uv_map="map1")
deformer.install_cbs()
# deformer.remove_cbs()