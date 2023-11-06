from typing import Union

from maya.api import OpenMaya


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
