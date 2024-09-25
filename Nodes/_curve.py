from __future__ import annotations

from maya.api import OpenMaya

from ..Helpers import point, utils

from ..Core import constants, _factory
from ..Nodes._shape import _Shape


@_factory.register()
class _Curve(_Shape):

    kApiType = OpenMaya.MFn.kNurbsCurve

    def _post_init(self):
        path = utils.get_path(self._object)
        self._mfn = OpenMaya.MFnNurbsCurve(path)
        self._modifier = OpenMaya.MDagModifier()
    
    def points(self, world: bool = True, normalize: bool = False) -> OpenMaya.MPointArray:
        space = constants.kWorld if world else constants.kObject
        output = self._mfn.cvPositions(space)
        if normalize:
            point.normalize(output)
        
        return output

    def set_points(self, points: OpenMaya.MPointArray, world: bool = True):    
        space = constants.kWorld if world else constants.kObject
        self._mfn.setCVPositions(points, space)
    
    def to_dict(self, normalize: bool = True) -> dict:
        data = {}
        points = self.points(normalize=normalize)
        data[constants.kType] = constants.kCurve
        data[constants.kPoints] = point.array_to_list(points)
        data[constants.kKnots] = list(self._mfn.knots())
        data[constants.kForm] = self._mfn.form
        data[constants.kDegrees] = self._mfn.degree

        return data

    @classmethod
    def from_dict(cls, data: dict, parent: str | OpenMaya.MObject,
                  shape_dir: int = None, scale: float = None):

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

        shape = OpenMaya.MFnNurbsCurve().create(points,
                                                knots,
                                                data.get(constants.kDegrees, 1),
                                                data.get(constants.kForm, 1),
                                                data.get(constants.k2D, False),
                                                data.get(constants.kRational, True),
                                                parent)

        return _factory.create(shape)
    
    def update(self):
        self._mfn.updateCurve()
