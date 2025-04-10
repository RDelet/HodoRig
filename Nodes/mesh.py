from __future__ import annotations
from dataclasses import asdict, dataclass, field
from functools import partial
from typing import Optional

from maya import cmds
from maya.api import OpenMaya

from ..Helpers import point, utils

from ..Core import constants, _factory
from .dagNode import DAGNode
from .shape import Shape


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


@_factory.register()
class Mesh(Shape):

    kApiType = OpenMaya.MFn.kMesh

    def _post_init(self):
        self._mfn = OpenMaya.MFnMesh(self._path)
        self._mit_vtx = OpenMaya.MItMeshVertex(self._path)
        self._mit_poly = OpenMaya.MItMeshPolygon(self._path)
        self._modifier = OpenMaya.MDagModifier()
    
    def points(self, world: bool = True, normalize: bool = False,
               vertex_ids: Optional[list] = None) -> OpenMaya.MPointArray:

        space = constants.kWorld if world else constants.kObject
        output = self._mfn.getPoints(space)
        
        if vertex_ids:
            points = OpenMaya.MPointArray()
            for vertex_id in vertex_ids:
                points.append(output[vertex_id])
            output = points
        
        if normalize:
            point.normalize(output)
        
        return output

    def set_points(self, points: OpenMaya.MPointArray, world: bool = True):
        space = constants.kWorld if world else constants.kObject
        self._mfn.setPoints(points, space)
    
    def uvs(self) -> list:
        data = []
        for name in self._mfn.getUVSetNames():
            uv = UV(name)
            data.append(uv)
            u, v = self._mfn.getUVs(name)
            uv.u = list(u)
            uv.v = list(v)
        
        return data

    def set_uvs(self, uv_data: list):
        uv_names = self._mfn.getUVSetNames()
        for data in uv_data:
            uv = UV(**data)
            print(uv)
            if uv.name not in uv_names:
                self._mfn.createUVSetWithName(uv.name)
            u = OpenMaya.MFloatArray(uv.u)
            v = OpenMaya.MFloatArray(uv.v)
            self._mfn.setUVs(u, v, uv.name)

    def components(self) -> OpenMaya.MObject:
        single_component = OpenMaya.MFnSingleIndexedComponent()
        component = single_component.create(OpenMaya.MFn.kMeshVertComponent)
        self._mit_vtx.reset()
        while not self._mit_vtx.isDone():
            single_component.addElement(self._mit_vtx.index())
            self._mit_vtx.next()

        return component
    
    def to_dict(self, normalize: bool = True) -> dict:
        data = {}
        self._mit_poly.reset()

        points = self.points(normalize=normalize)

        poly_counts = []
        poly_connects = []
        while not self._mit_poly.isDone():
            vertices = self._mit_poly.getVertices()
            poly_counts.append(len(vertices))
            for i in range(len(vertices)):
                poly_connects.append(vertices[i])
            self._mit_poly.next()

        data[constants.kType] = constants.kMesh
        data[constants.kNumVertices] = self._mfn.numVertices
        data[constants.kNumPolygons] = self._mfn.numPolygons
        data[constants.kPoints] = point.array_to_list(points)
        data[constants.kPolygonCounts] = poly_counts
        data[constants.kPolygonConnects] = poly_connects
        data[constants.kUv] = [x.to_dict() for x in self.uvs()]

        return data

    @classmethod
    def from_dict(cls, data: dict, parent: str | OpenMaya.MObject | DAGNode,
                  shape_dir: int = None, scale: float = None):
        if isinstance(parent, DAGNode):
            parent = parent.object

        points = OpenMaya.MPointArray(data.get(constants.kPoints, []))
        if len(points) == 0:
            raise RuntimeError('Invalid shape data !')

        if shape_dir is not None:
            point.orient(points, shape_dir)
        if scale is not None:
            point.orient(points, scale)

        poly_counts = OpenMaya.MIntArray(data.get(constants.kPolygonCounts, []))
        poly_connects = OpenMaya.MIntArray(data.get(constants.kPolygonConnects, []))
        if poly_counts is None or poly_connects is None:
            raise Exception("Invalid mesh data.")

        shape = OpenMaya.MFnMesh().create(points,
                                          poly_counts,
                                          poly_connects,
                                          OpenMaya.MFloatArray(),
                                          OpenMaya.MFloatArray(),
                                          parent)

        new_node = _factory.create(shape)
        if parent is not None:
            new_node.rename(f"{utils.name(parent, False, False)}Shape")

        uv_data = data.get(constants.kUv)
        if uv_data:
            new_node.set_uvs(uv_data)
        
        cmds.sets(new_node.name, edit=True, forceElement='initialShadingGroup')

        return new_node
    
    def update(self):
        self._mfn.updateSurface()
