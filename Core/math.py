from typing import Union
import numpy as np

from maya.api import OpenMaya


def area_triangle(pa: np.array, pb: np.array, pc: np.array):
    return 0.5 * np.linalg.norm(np.cross(pb - pa, pc - pa))


def barycentric_coordinate(point, a, b, c):
    abc = area_triangle(a, b, c)
    pbc = area_triangle(point, b, c)
    apc = area_triangle(a, point, c)
    abp = area_triangle(a, b, point)

    return round(pbc / abc, 3), round(apc / abc, 3), round(abp / abc, 3)


def centroid(points: Union[OpenMaya.MVectorArray, OpenMaya.MPointArray]) -> OpenMaya.MVector:
    output = OpenMaya.MVector()
    for point in points:
        output += OpenMaya.MVector(point)
    output /= points.length()

    return output


def weighted_centroid(points: Union[OpenMaya.MVectorArray, OpenMaya.MPointArray],
                      weights: list, weight_tolerence: float = 1e-6) -> OpenMaya.MVector:

    if len(points) != len(weights):
        raise RuntimeError("Mismatch number of element between points and weights !")
    
    output = OpenMaya.MVector()
    weight_sum = 0.0
    for point, weight in zip(points, weights):
        if weight >= weight_tolerence:
            weight_sum += weight
            output += OpenMaya.MVector(point * weight)
    output /= weight_sum

    return output


def distance_between(nodes: list) -> float:
    distance = 0.0
    for i in range(len(nodes) - 1):
        distance += abs((nodes[i + 1] - nodes[i]).lenth())
    
    return distance


def project_from_matrix(matrix: OpenMaya.MMatrix, direction: int, distance: float) -> OpenMaya.MVector:
    return


def sign(dir_index: int) -> float:
    """!@Brief Get sign for dir index."""
    return 1.0 if dir_index % 2 == 0 else -1.0


def absolute_dir(dir_index: int) -> int:
    """!@Brief Get absolute dir index.
               direction can be X, -X, Y, -Y, Z, -Z. Here we get only X, Y, Z
    """
    return abs(int(dir_index / 2))
