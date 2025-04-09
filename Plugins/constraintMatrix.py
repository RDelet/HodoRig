from __future__ import annotations
from typing import Tuple
from enum import Enum

import logging
import numpy as np
import traceback

from maya.api import OpenMaya


log = logging.getLogger("constraintMatrix")
log.setLevel(logging.DEBUG)


def maya_useNewAPI():
    """!@Brief Maya API 2.0"""
    pass


class ConstraintType(Enum):
    PARENT = 0
    POINT = 1
    ORIENT = 2
    SCALE = 3
    FULL = 4


class RotateOrder(Enum):
    XYZ = 0
    YZX = 1
    ZXY = 2
    XZY = 3
    YXZ = 4
    ZYX = 5


def decompose_matrix(matrix: np.array) -> Tuple[np.array]:
    """!@Brief Transformation matrix decomposition."""
    translation = matrix[:3, 3].copy()
    M = matrix[:3, :3].copy()
    
    # Extract first coloumn
    col0 = M[:, 0]
    scale_x = np.linalg.norm(col0)
    if scale_x == 0:
        raise ValueError("Scale X nul")
    R0 = col0 / scale_x
    # Extract second coloumn
    col1 = M[:, 1]
    shear_xy = np.dot(R0, col1)
    col1_ortho = col1 - shear_xy * R0
    scale_y = np.linalg.norm(col1_ortho)
    if scale_y == 0:
        raise ValueError("Scale Y nul")
    R1 = col1_ortho / scale_y
    # Extract theird coloumn
    col2 = M[:, 2]
    shear_xz = np.dot(R0, col2)
    col2_temp = col2 - shear_xz * R0
    shear_yz = np.dot(R1, col2_temp)
    col2_ortho = col2_temp - shear_yz * R1
    scale_z = np.linalg.norm(col2_ortho)
    if scale_z == 0:
        raise ValueError("Scale Z nul")
    R2 = col2_ortho / scale_z
    # Compute rotation matrix from axis extraction
    R = np.column_stack((R0, R1, R2))
    # Reflexion correction
    if np.linalg.det(R) < 0:
        scale_z *= -1
        R2 *= -1
        R = np.column_stack((R0, R1, R2))
    
    scale = np.array([scale_x, scale_y, scale_z])
    shear = np.array([shear_xy, shear_xz, shear_yz])

    return translation, R, scale, shear


def matrix_to_quaternion(matrix: np.array) -> np.array:
    """!@Brief convert rotation matrix to quaternion."""

    m00, m01, m02 = matrix[0,0], matrix[0,1], matrix[0,2]
    m10, m11, m12 = matrix[1,0], matrix[1,1], matrix[1,2]
    m20, m21, m22 = matrix[2,0], matrix[2,1], matrix[2,2]
    trace = m00 + m11 + m22

    if trace > 0:
        s = 0.5 / np.sqrt(trace + 1.0)
        w = 0.25 / s
        x = (m21 - m12) * s
        y = (m02 - m20) * s
        z = (m10 - m01) * s
    else:
        if (m00 > m11) and (m00 > m22):
            s = 2.0 * np.sqrt(1.0 + m00 - m11 - m22)
            w = (m21 - m12) / s
            x = 0.25 * s
            y = (m01 + m10) / s
            z = (m02 + m20) / s
        elif m11 > m22:
            s = 2.0 * np.sqrt(1.0 + m11 - m00 - m22)
            w = (m02 - m20) / s
            x = (m01 + m10) / s
            y = 0.25 * s
            z = (m12 + m21) / s
        else:
            s = 2.0 * np.sqrt(1.0 + m22 - m00 - m11)
            w = (m10 - m01) / s
            x = (m02 + m20) / s
            y = (m12 + m21) / s
            z = 0.25 * s

    return np.array([w, x, y, z])


def quaternion_to_matrix(q: np.array) -> np.array:
    """!@Brief Convert a quaternion to rotation matrix (3*3)"""
    w, x, y, z = q
    return np.array([[1 - 2*(y*y + z*z),   2*(x*y - z*w), 2*(x*z + y*w)],
                    [2*(x*y + z*w), 1 - 2*(x*x + z*z), 2*(y*z - x*w)],
                    [2*(x*z - y*w), 2*(y*z + x*w), 1 - 2*(x*x + y*y)]])


def matrix_to_euler(matrix, rotateOrder=RotateOrder.XYZ):
    """!@Brief Convert a matrix to euler angle"""

    def safe_asin(x):
        return np.arcsin(np.clip(x, -1.0, 1.0))
    
    if rotateOrder == RotateOrder.ZYX:
        rx = np.arctan2(matrix[2, 1], matrix[2, 2])
        ry = safe_asin(-matrix[2, 0])
        rz = np.arctan2(matrix[1, 0], matrix[0, 0])
        return np.array([rx, ry, rz])
    elif rotateOrder == RotateOrder.XYZ:
        ry = safe_asin(matrix[0, 2])
        rx = np.arctan2(-matrix[1, 2], matrix[2, 2])
        rz = np.arctan2(-matrix[0, 1], matrix[0, 0])
        return np.array([rx, ry, rz])
    elif rotateOrder == RotateOrder.YZX:
        rz = np.arctan2(matrix[1, 2], matrix[1, 1])
        ry = safe_asin(-matrix[1, 0])
        rx = np.arctan2(matrix[2, 0], matrix[0, 0])
        return np.array([rx, ry, rz])
    elif rotateOrder == RotateOrder.ZXY:
        rx = np.arctan2(-matrix[2, 1], matrix[2, 2])
        rz = np.arctan2(-matrix[0, 1], matrix[1, 1])
        ry = safe_asin(matrix[2, 0])
        return np.array([rx, ry, rz])
    elif rotateOrder == RotateOrder.XZY:
        rz = np.arctan2(matrix[0, 2], matrix[0, 0])
        rx = safe_asin(-matrix[0, 1])
        ry = np.arctan2(matrix[2, 1], matrix[1, 1])
        return np.array([rx, ry, rz])
    elif rotateOrder == RotateOrder.YXZ:
        rx = safe_asin(matrix[2, 0])
        ry = np.arctan2(-matrix[2, 1], matrix[2, 2])
        rz = np.arctan2(-matrix[1, 0], matrix[0, 0])
        return np.array([rx, ry, rz])
    
    raise ValueError(f"Invalid rotate order given : {rotateOrder}")



def weighted_average_quaternions(rotations: np.array, weights: list) -> np.array:
    """ !@Brief Average multiple quaternions with specific weights.

    Sources:
        - https://github.com/christophhagen/averaging-quaternions/blob/master/averageQuaternions.py
        - https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/20070017872.pdf
    """
    a = np.zeros(shape=(4, 4))
    accum = np.zeros(4)
    for rotation, weight in zip(rotations, weights):
        q = np.array(rotation)
        if np.dot(accum, q) < 0.0:
            accum -= weight * q
            q *= -1
        else:
            accum += weight * q
        a += weight * np.outer(q, q)

    a /= sum(weights)
    eigen_values, eigen_vectors = np.linalg.eig(a)
    eigen_vectors = eigen_vectors[:, eigen_values.argsort()[::-1]]

    return np.real(eigen_vectors[:, 0])


def average_rotation_matrices(rotations, weights):
    R_sum = np.zeros((3, 3))
    for R, w in zip(rotations, weights):
        R_sum += w * R
    # Projection sur SO(3) via SVD
    U, s, Vt = np.linalg.svd(R_sum)
    R_avg = np.dot(U, Vt)
    # Correction : dans le cas où le déterminant est négatif, on ajuste pour rester dans SO(3)
    if np.linalg.det(R_avg) < 0:
        U[:, -1] *= -1
        R_avg = np.dot(U, Vt)
    
    return R_avg


def binomial_coefficient(n, k):
    """
    Calcule le coefficient binomial (n choisir k) de façon efficace.
    Cette implémentation évite les débordements pour les grands nombres.
    """
    if k < 0 or k > n:
        return 0
    if k == 0 or k == n:
        return 1
    
    # Optimisation: utiliser la symétrie de C(n,k) = C(n,n-k)
    k = min(k, n - k)
    
    # Calcul par multiplication progressive
    result = 1
    for i in range(k):
        result = result * (n - i) // (i + 1)
    
    return result


def weighted_mean(array: np.array, weights: np.array) -> np.array:
    return np.average(array, axis=0, weights=weights)


def weighted_geometric_mean(array: np.array, weights: np.array) -> np.ndarray:
    normalized_weights = weights / np.sum(weights)
    return np.prod(array ** normalized_weights[:, np.newaxis], axis=0)


def orient_constraint(matrices: np.array, weights: np.array) -> np.array:
    R = np.eye(4)
    R[:3, :3] = average_rotation_matrices(matrices, weights)
    
    return R


def point_constraint(translations: np.array, weights: np.array) -> np.array:
    T = np.eye(4)
    T[:3, 3] = weighted_mean(translations, weights)

    return T


def scale_constraint(scales: np.array, weights: np.array) -> np.array:
    scale = weighted_geometric_mean(scales, weights)

    S = np.eye(4)
    S[0, 0] = scale[0]
    S[1, 1] = scale[1]
    S[2, 2] = scale[2]

    return S


def average_matrix(matrices: np.array, weights: np.array, cst_type: ConstraintType) -> np.array:
    translations = []
    rotations = []
    scales = []
    for matrix in matrices:
        translation, rotation, scale, _ = decompose_matrix(matrix)
        translations.append(translation)
        rotations.append(rotation)
        scales.append(scale)

    if cst_type == ConstraintType.PARENT:
        T = point_constraint(translations, weights)
        R = orient_constraint(rotations, weights)
        return T @ R
    elif cst_type == ConstraintType.POINT:
        return point_constraint(translations, weights)
    elif cst_type == ConstraintType.ORIENT:
        return orient_constraint(rotations, weights)
    elif cst_type == ConstraintType.SCALE:
        return scale_constraint(scales, weights)
    elif cst_type == ConstraintType.FULL:
        T = point_constraint(translations, weights)
        R = orient_constraint(rotations, weights)
        S = scale_constraint(scales, weights)
        return T @ R @ S
    else:
        raise RuntimeError("Invalid constraint type given !")


class ConstraintMatrix(OpenMaya.MPxNode):

    kPluginNode = "constraintMatrix"
    kPluginNodeID = OpenMaya.MTypeId(0x1851301)
    kPluginNodeType = OpenMaya.MPxNode.kDependNode

    CONSTRAINT_TYPE = OpenMaya.MObject()
    WEIGHT = OpenMaya.MObject()
    MATRIX = OpenMaya.MObject()
    OFFSET = OpenMaya.MObject()
    SOURCE = OpenMaya.MObject()
    PARENT_MATRIX = OpenMaya.MObject()

    OUTPUT_MATRIX = OpenMaya.MObject()

    def __init__(self):
        super().__init__()

        self._type = 0
        self._parent_matrix = OpenMaya.MMatrix()
        self._sources = []
        self._weights = []

    @classmethod
    def creator(cls):
        return cls()

    def compute(self, plug, data):
        if plug != self.OUTPUT_MATRIX and plug.isConnected:
            return

        self._get_data(data)
        if len(self._sources) == 0:
            return

        self._set_matrix(plug, data, self._compute_matrix())


    def _get_data(self, data):
        self._type = ConstraintType(data.inputValue(self.CONSTRAINT_TYPE).asShort())
        self._parent_matrix = np.array(data.inputValue(self.PARENT_MATRIX).asMatrix()).reshape(4, 4)

        sources = []
        weights = []
        sources_handle = data.inputArrayValue(self.SOURCE)
        while not sources_handle.isDone():
            source_handle = sources_handle.inputValue()
            matrix = source_handle.child(self.MATRIX).asMatrix()
            offset = source_handle.child(self.OFFSET).asMatrix()
            sources.append(np.array(offset * matrix).reshape(4, 4).T)
            weights.append(source_handle.child(self.WEIGHT).asFloat())
            sources_handle.next()

        self._sources = np.array(sources)
        self._weights = np.array(weights)

    def _compute_matrix(self):
        return self._parent_matrix @ average_matrix(self._sources, self._weights, self._type).T

    def _set_matrix(self, plug: OpenMaya.MPlug, data: OpenMaya.MDataBlock, output_matrix: np.array):
        if plug == self.OUTPUT_MATRIX:
            handle = data.outputValue(self.OUTPUT_MATRIX)
            handle.setMMatrix(OpenMaya.MMatrix(output_matrix.flatten()))
            handle.setClean()

    @classmethod
    def initializer(cls):

        in_attributes = []
        out_attributes = []

        # Input attributes
        enum_attr = OpenMaya.MFnEnumAttribute()
        cls.CONSTRAINT_TYPE = enum_attr.create("constraintType", "constraintType", 0)
        for i, name in enumerate([t.name.title() for t in ConstraintType]):
            enum_attr.addField(name, i)
        enum_attr.storable = True
        enum_attr.keyable = False
        in_attributes.append(cls.CONSTRAINT_TYPE)

        weight_attr = OpenMaya.MFnNumericAttribute()
        cls.WEIGHT = weight_attr.create("weight", "weight", OpenMaya.MFnNumericData.kFloat, 1.0)
        weight_attr.storable = True
        weight_attr.keyable = True

        matrix_attr = OpenMaya.MFnMatrixAttribute()
        cls.MATRIX = matrix_attr.create("matrix", "matrix", OpenMaya.MFnMatrixAttribute.kDouble)
        matrix_attr.storable = True
        matrix_attr.keyable = True

        offset_attr = OpenMaya.MFnMatrixAttribute()
        cls.OFFSET = offset_attr.create("offset", "offset", OpenMaya.MFnMatrixAttribute.kDouble)
        offset_attr.storable = True
        offset_attr.keyable = True

        source_attr = OpenMaya.MFnCompoundAttribute()
        cls.SOURCE = source_attr.create("source", "source")
        source_attr.addChild(cls.WEIGHT)
        source_attr.addChild(cls.MATRIX)
        source_attr.addChild(cls.OFFSET)
        source_attr.storable = True
        source_attr.keyable = True
        source_attr.array = True
        in_attributes.append(cls.SOURCE)

        parent_matrix_attr = OpenMaya.MFnMatrixAttribute()
        cls.PARENT_MATRIX = parent_matrix_attr.create("parentMatrix", "parentMatrix",
                                                      OpenMaya.MFnMatrixAttribute.kDouble)
        parent_matrix_attr.storable = True
        parent_matrix_attr.keyable = True
        in_attributes.append(cls.PARENT_MATRIX)

        # Output attributes
        output_matrix_attr = OpenMaya.MFnMatrixAttribute()
        cls.OUTPUT_MATRIX = output_matrix_attr.create("outputMatrix", "outputMatrix",
                                                      OpenMaya.MFnMatrixAttribute.kDouble)
        output_matrix_attr.storable = False
        output_matrix_attr.keyable = False
        out_attributes.append(cls.OUTPUT_MATRIX)

        # Add attributes
        for i, attribute in enumerate(in_attributes + out_attributes):
            cls.addAttribute(attribute)

        # Attributes affects
        for out_attr in out_attributes:
            for in_attr in in_attributes:
                cls.attributeAffects(in_attr, out_attr)


# noinspection PyPep8Naming
def initializePlugin(obj: OpenMaya.MObject):
    plugin = OpenMaya.MFnPlugin(obj, "Remi Deletrain -- remi.deletrain@gmail.com", "1.0", "Any")
    try:
        plugin.registerNode(ConstraintMatrix.kPluginNode,
                            ConstraintMatrix.kPluginNodeID,
                            ConstraintMatrix.creator,
                            ConstraintMatrix.initializer,
                            ConstraintMatrix.kPluginNodeType)
    except Exception:
        log.debug(traceback.format_exc())
        raise RuntimeError(f"Failed to register command: {ConstraintMatrix.kPluginNode}")


# noinspection PyPep8Naming
def uninitializePlugin(obj: OpenMaya.MObject):
    plugin = OpenMaya.MFnPlugin(obj)
    try:
        plugin.deregisterNode(ConstraintMatrix.kPluginNodeID)
    except Exception:
        log.debug(traceback.format_exc())
        raise RuntimeError(f"Failed to register command: {ConstraintMatrix.kPluginNode}")
