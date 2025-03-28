from __future__ import annotations
import numpy as np

from maya.api import OpenMaya

from ..Core import constants as cst, _factory
from ..Core.logger import log
from ..Helpers import point, utils
from .node import Node
from .dagNode import DAGNode
from .shape import Shape


@_factory.register()
class Curve(Shape):

    kApiType = OpenMaya.MFn.kNurbsCurve

    def _post_init(self):
        self._mfn = OpenMaya.MFnNurbsCurve(self._path)
        self._modifier = OpenMaya.MDagModifier()
    
    def points(self, world: bool = True, normalize: bool = False) -> OpenMaya.MPointArray:
        space = cst.kWorld if world else cst.kObject
        output = self._mfn.cvPositions(space)
        if normalize:
            point.normalize(output)
        
        return output
    
    @classmethod
    def create_from_points(cls, name: str, points: OpenMaya.MPointArray | np.array | list | tuple,
                          degree: int = 3, form: int = OpenMaya.MFnNurbsCurve.kOpen,
                          is_2d: bool = False, is_rational: bool = True, is_uniform: bool = True,
                          parent: str | OpenMaya.MObject | DAGNode = None) -> Curve:
        if isinstance(parent, DAGNode):
            parent = parent.object
        elif isinstance(parent, str):
            parent = utils.get_object(parent)
        elif parent is None:
            parent = utils.create(cst.kTransform, name)

        if not isinstance(points, OpenMaya.MPointArray):
            points = OpenMaya.MPointArray(points)

        curve_obj = OpenMaya.MFnNurbsCurve().createWithEditPoints(points, degree, form,
                                                                  is_2d, is_rational,
                                                                  is_uniform, parent)
        utils.rename(curve_obj, f"{name}Shape")

        return cls(curve_obj)

    def param_at_point(self, point: OpenMaya.MPoint | np.array | list | tuple,
                       tolerence: float = 1e-4, space: int = OpenMaya.MSpace.kWorld) -> float:
        if not isinstance(point, OpenMaya.MPoint):
            point = OpenMaya.MPoint(point)
        try:
            return self._mfn.getParamAtPoint(point, tolerence, space)
        except RuntimeError:
            log.warning(f"Point {point} is out of tolerence.")
            return 0.0
    
    def create_poci(self, parameter: float, name: str = None,
                    turn_on_percentage: bool = False) -> Node:
        if not self.is_valid():
            raise RuntimeError("Invalid curve object !")

        poci = Node.create(cst.kPointOnCurveInfo, name)
        poci.set_attribute(cst.kParameter, parameter)
        poci.set_attribute(cst.kTurnOnPercentage, turn_on_percentage)
        self.connect_to(cst.kLocal, f"{poci}.{cst.kInputCurve}")

        return poci

    def set_points(self, points: OpenMaya.MPointArray, world: bool = True):    
        space = cst.kWorld if world else cst.kObject
        self._mfn.setCVPositions(points, space)
    
    def to_dict(self, normalize: bool = True) -> dict:
        data = {}
        points = self.points(normalize=normalize)
        data[cst.kType] = cst.kCurve
        data[cst.kPoints] = point.array_to_list(points)
        data[cst.kKnots] = list(self._mfn.knots())
        data[cst.kForm] = self._mfn.form
        data[cst.kDegrees] = self._mfn.degree

        return data

    @classmethod
    def from_dict(cls, data: dict, parent: str | OpenMaya.MObject | DAGNode,
                  shape_dir: int = None, scale: float = None):
        if isinstance(parent, DAGNode):
            parent = parent.object

        points = OpenMaya.MPointArray(data.get(cst.kPoints, []))
        if len(points) == 0:
            raise RuntimeError('Invalid shape data !')

        if shape_dir is not None:
            point.orient(points, shape_dir)
        if scale is not None:
            point.scale(points, scale)

        knots = OpenMaya.MDoubleArray(data.get(cst.kKnots, []))
        if len(knots) == 0:
            knots = OpenMaya.MDoubleArray([float(i) for i in range(len(points))])

        shape = OpenMaya.MFnNurbsCurve().create(points,
                                                knots,
                                                data.get(cst.kDegrees, 1),
                                                data.get(cst.kForm, 1),
                                                data.get(cst.k2D, False),
                                                data.get(cst.kRational, True),
                                                parent)
        
        new_node = _factory.create(shape)
        if parent is not None:
            new_node.rename(f"{utils.name(parent, False, False)}Shape")

        return new_node
    
    def update(self):
        self._mfn.updateCurve()
