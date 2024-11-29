from typing import Union

from maya.api import OpenMaya

"""
ToDo: Use numpy !
"""


def array_to_list(points: Union[OpenMaya.MVectorArray, OpenMaya.MPointArray]) -> list:
    return [list(p) for p in points]


def normalize(points: Union[OpenMaya.MVectorArray, OpenMaya.MPointArray]) -> list:
    f_max = max([abs(item) for sublist in points for item in sublist])
    for i in range(len(points)):
        points[i] /= f_max


def _orient(point: OpenMaya.MPoint, shape_dir: int) -> OpenMaya.MPoint:
    """!@Brief Orient point from shape direction."""
    if shape_dir == 0:
        return OpenMaya.MPoint(point.y, point.x, point.z)
    elif shape_dir == 1:
        return OpenMaya.MPoint(point.y, point.x, point.z) * -1
    elif shape_dir == 2:
        return point
    elif shape_dir == 3:
        return point * -1
    elif shape_dir == 4:
        return OpenMaya.MPoint(point.x, point.z, point.y)
    elif shape_dir == 5:
        return OpenMaya.MPoint(point.x, point.z, point.y) * -1
    else:
        raise Exception("Invalid front int given.")


def orient(points: OpenMaya.MPointArray, shape_dir: int):
    """!@Brief Orient points from shape direction."""
    for i in range(len(points)):
        points[i] = _orient(points[i], shape_dir)


def scale(points: OpenMaya.MPointArray, scale: float):
    """!@Brief Scale points."""
    for i in range(len(points)):
        points[i] *= scale


def project_on_plane():
    pass


def priject_on_line():
    pass
