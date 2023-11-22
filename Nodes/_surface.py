from __future__ import annotations

from maya.api import OpenMaya

from HodoRig.Core import constants, _factory, point, utils
from HodoRig.Nodes._shape import _Shape


@_factory.register()
class _Surface(_Shape):

    kApiType = OpenMaya.MFn.kNurbsSurface

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
    
    def get_cvs_component(self, shape: str | OpenMaya.MObject,
                          use_u_rows: bool = False) -> OpenMaya.MObject:
        double_component = OpenMaya.MFnDoubleIndexedComponent()
        component = double_component.create(OpenMaya.MFn.kSurfaceCVComponent)
        u_count = self._mfn.numCVsInU
        v_count = self._mfnmfn.numCVsInV
        for _ in range(u_count):
            for _ in range(v_count):
                args = (v_count, u_count) if use_u_rows else (u_count, v_count)
                double_component.addElement(*args)

        return component
    
    def to_dict(self, normalize: bool = True) -> dict:
        data = dict()
        points = points(normalize=normalize)
        data[constants.kType] = constants.kSurface
        data[constants.kPoints] = point.array_to_list(points)
        data[constants.kKnotsU] = list(self._mfn.knotsInU())
        data[constants.kKnotsV] = list(self._mfn.knotsInV())
        data[constants.kFormU] = self._mfn.formInU
        data[constants.kFormV] = self._mfn.formInV
        data[constants.kDegreeU] = self._mfn.degreeU
        data[constants.kDegreeV] = self._mfn.degreeV

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
            point.orient(points, scale)

        knots_u = OpenMaya.MDoubleArray(data.get(constants.kKnotsU, []))
        if len(knots_u) == 0:
            knots_u = OpenMaya.MDoubleArray([float(i) for i in range(len(points))])
        knots_V = OpenMaya.MDoubleArray(data.get(constants.kKnotsV, []))
        if len(knots_V) == 0:
            knots_V = OpenMaya.MDoubleArray([float(i) for i in range(len(points))])

        shape = OpenMaya.MFnNurbsSurface().create(points,
                                                  knots_u,
                                                  knots_V,
                                                  data.get(constants.kDegreeU, 1),
                                                  data.get(constants.kDegreeV, 1),
                                                  data.get(constants.kFormU, 1),
                                                  data.get(constants.kFormV, 1),
                                                  data.get(constants.kRational, False),
                                                  parent)

        return _factory.create(shape)
    
    def update(self):
        self._mfn.updateSurface()
