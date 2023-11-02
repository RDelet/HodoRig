from typing import Union

from maya.api import OpenMaya

from HodoRig.Core import constants, point, utils


kNodeType = constants.kSurface


def shape_to_dict(node: Union[str, OpenMaya.MObject], normalize: bool = True) -> dict:
    """!@Brief Get NurbsSurface shape data."""

    data = dict()

    if not isinstance(node, OpenMaya.MObject):
        raise TypeError(f"Argument must be a MObject not {type(node)} !")
    if not node.hasFn(OpenMaya.MFn.kNurbsSurface):
        raise TypeError(f"Node must be a kurbsSurface not {node.apiTypeStr()}")

    mfn = OpenMaya.MFnNurbsSurface(node)

    points = mfn.cvPositions(OpenMaya.MSpace.kObject)
    point.normalize(points)    

    data[constants.kType] = kNodeType
    data[constants.kPoints] = point.array_to_list(points)
    data[constants.kKnotsU] = list(mfn.knotsInU())
    data[constants.kKnotsV] = list(mfn.knotsInV())
    data[constants.kFormU] = mfn.formInU
    data[constants.kFormV] = mfn.formInV
    data[constants.kDegreeU] = mfn.degreeU
    data[constants.kDegreeV] = mfn.degreeV

    return data


def dict_to_shape(data: dict, parent: OpenMaya.MObject, shape_dir: int = None, scale: float = None) -> OpenMaya.MObject:
    """!@Brief Build NurbsSurface shape."""

    points = OpenMaya.MPointArray(data.get(constants.kPoints, []))
    if len(points) == 0:
        raise RuntimeError('Invalid shape data !')
    
    if shape_dir is not None:
        point.orient(points, shape_dir)
    if scale is not None:
        point.orient(points, scale)

    knots_u = OpenMaya.MDoubleArray(data.get(constants.kKnotsU, []))
    if len(knots_u) == 0:
        knots_u = OpenMaya.MDoubleArray([float(i) for i in range(len(points))])

    knots_V = OpenMaya.MDoubleArray(data.get(constants.kKnotsV, []))
    if len(knots_V) == 0:
        knots_V = OpenMaya.MDoubleArray([float(i) for i in range(len(points))])

    return OpenMaya.MFnNurbsSurface().create(
        points,
        knots_u,
        knots_V,
        data.get(constants.kDegreeU, 1),
        data.get(constants.kDegreeV, 1),
        data.get(constants.kFormU, 1),
        data.get(constants.kFormV, 1),
        data.get(constants.kRational, False),
        parent
    )