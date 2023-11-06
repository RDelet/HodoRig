import dataclasses
from dataclasses import dataclass, field
from functools import partial
from typing import Union

from maya.api import OpenMaya

from HodoRig.Core import constants, point, utils


kNodeType = constants.kMesh
kWorld = OpenMaya.MSpace.kWorld
kObject = OpenMaya.MSpace.kObject


def get_points(node: Union[str, OpenMaya.MObject, OpenMaya.MDagPath],
               world: bool = True, vertex_ids: list = None) -> OpenMaya.MPointArray:
    """!@Brief Get mesh point."""
    if isinstance(node, str):
        node = utils.get_path(node)
    if isinstance(node, OpenMaya.MObject) and world:
        raise RuntimeError('Impossible to get world position with MObject !')

    mfn = OpenMaya.MFnMesh(node)
    output = mfn.getPoints(space)
    space = kWorld if world else kObject

    if vertex_ids:
        points = OpenMaya.MPointArray()
        for vertex_id in vertex_ids:
            points.append(output[vertex_id])
        output = points

    return output


def shape_to_dict(node: Union[str, OpenMaya.MObject], normalize: bool = True) -> dict:
    """!@Brief Get Mesh shape data."""

    data = dict()

    if isinstance(node, str):
        node = utils.get_object(node)
    if not node.hasFn(OpenMaya.MFn.kMesh):
        raise TypeError(f"fNode must be a kurbsSurface not {node.apiTypeStr()} !")

    mfn = OpenMaya.MFnMesh(node)
    mit = OpenMaya.MItMeshPolygon(node)

    points = mfn.getPoints(kObject)
    point.normalize(points)

    poly_counts = list()
    poly_connects = list()
    while not mit.isDone():
        vertices = mit.getVertices()
        poly_counts.append(len(vertices))
        for i in range(len(vertices)):
            poly_connects.append(vertices[i])
        mit.next()

    data[constants.kType] = kNodeType
    data[constants.kNumVertices] = mfn.numVertices
    data[constants.kNumPolygons] = mfn.numPolygons
    data[constants.kPoints] = point.array_to_list(points)
    data[constants.kPolygonCounts] = poly_counts
    data[constants.kPolygonConnects] = poly_connects
    data[constants.kUv] = [dataclasses.asdict(x) for x in get_uv(node)]

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

    poly_counts = OpenMaya.MIntArray(data.get(constants.kPolygonCounts, []))
    poly_connects = OpenMaya.MIntArray(data.get(constants.kPolygonConnects, []))
    if poly_counts is None or poly_connects is None:
        raise Exception("Invalid mesh data.")

    shape = OpenMaya.MFnMesh().create(
        data.get(constants.kNumVertices),
        data.get(constants.kNumPolygons),
        points,
        poly_counts,
        poly_connects,
        parent
    )

    uv_data = data.get(constants.kUv)
    if uv_data:
        set_uv(shape, uv_data)

    return shape


@dataclass
class UV(object):
    
    name: str
    u: list = field(default_factory=partial(list))
    v: list = field(default_factory=partial(list))

    @property
    def count(self) -> int:
        return len(self.u)


def get_uv(node: Union[str, OpenMaya.MObject]) -> list:
    """!@Brief Get Mesh uv."""

    if isinstance(node, str):
        node = utils.get_object(node)
    if not node.hasFn(OpenMaya.MFn.kMesh):
        raise TypeError(f"fNode must be a mesh not {node.apiTypeStr()} !")

    mfn = OpenMaya.MFnMesh(node)
    uv_names = mfn.getUVSetNames()

    data = []
    for name in uv_names:
        uv = UV(name)
        data.append(uv)
        u, v = mfn.getUVs(name)
        uv.u = list(u)
        uv.v = list(v)
    
    return data


def set_uv(node: Union[str, OpenMaya.MObject], uv_data: list):
    
    if isinstance(node, str):
        node = utils.get_object(node)
    if not node.hasFn(OpenMaya.MFn.kMesh):
        raise TypeError(f"Node must be a mesh not {node.apiTypeStr()} !")

    uv_names = []
    mfn = OpenMaya.MFnMesh(node)
    mfn.getUVSetNames(uv_names)

    for uv in uv_data:
        if uv.name not in uv_names:
            mfn.createUVSetWithName(uv.name)

        u = OpenMaya.MFloatArray(uv.u)
        v = OpenMaya.MFloatArray(uv.v)
        mfn.setUVs(u, v, uv.name)


def get_vertex_component(node: Union[str, OpenMaya.MObject],) -> OpenMaya.MObject:
    """!@Brief Get mesh vertex at component object."""
    if isinstance(node, str):
        node = utils.get_object(node)

    single_component = OpenMaya.MFnSingleIndexedComponent()
    component = single_component.create(OpenMaya.MFn.kMeshVertComponent)

    mit = OpenMaya.MItMeshVertex(node)
    while not mit.isDone():
        single_component.addElement(mit.index())
        mit.next()

    return component
