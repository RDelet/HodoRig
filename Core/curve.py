from typing import Union

from maya.api import OpenMaya

from HodoRig.Core import constants, point, utils


kNodeType = constants.kCurve


def shape_to_dict(node: Union[str, OpenMaya.MObject], normalize: bool = True) -> dict:
    """!@Brief Get NurbsCurve shape data."""

    data = dict()

    if isinstance(node, str):
        node = utils.get_object(node)
    if not node.hasFn(OpenMaya.MFn.kNurbsCurve):
        raise TypeError(f"Node must be a NurbsCurve not {node.apiTypeStr()}")

    mfn = OpenMaya.MFnNurbsCurve(node)

    points = mfn.cvPositions(OpenMaya.MSpace.kObject)
    point.normalize(points)

    data[constants.kType] = kNodeType
    data[constants.kPoints] = point.array_to_list(points)
    data[constants.kKnots] = list(mfn.knots())
    data[constants.kForm] = mfn.form
    data[constants.kDegrees] = mfn.degree

    return data


def dict_to_shape(data: dict, parent: OpenMaya.MObject, shape_dir: int = None, scale: float = None) -> OpenMaya.MObject:
    """!@Brief Build NurbsCurve shape."""

    points = OpenMaya.MPointArray(data.get(constants.kPoints, []))
    if len(points) == 0:
        raise RuntimeError('Invalid shape data !')

    if shape_dir is not None:
        point.orient(points, shape_dir)
    if scale is not None:
        point.scale(points, scale)

    knots = OpenMaya.MDoubleArray(data.get(constants.kKnots, []))
    if len(knots) == 0:
        knots = OpenMaya.MDoubleArray([float(i) for i in range(len(points))])

    return OpenMaya.MFnNurbsCurve().create(
        points,
        knots,
        data.get(constants.kDegrees, 1),
        data.get(constants.kForm, 1),
        data.get(constants.k2D, False),
        data.get(constants.kRational, True),
        parent
    )