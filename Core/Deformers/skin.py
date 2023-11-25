import json
import os
from typing import Union

from maya import cmds
from maya.api import OpenMaya, OpenMayaAnim

from HodoRig.Core import math, utils
from HodoRig.Core.logger import log
from HodoRig.Core.Deformers.deformer import Deformer
from HodoRig.Nodes.node import Node


class Skin(Deformer):

    kName = "name"
    kInfluencesIDs = "influencesIDs"
    kInfluencesNames = "influencesNames"
    kSkinningMethod = "skinningMethod"
    kUseComponents = "useComponents"
    kDeformUserNormals = 'deformUserNormals'
    kDqsSupportNonRigid = 'dqsSupportNonRigid'
    kDqsScale = 'dqsScale'
    kNormalizeWeights = 'normalizeWeights'
    kWeightDistribution = 'weightDistribution'
    kMaxInfluences = "maxInfluences"
    kMaintainMaxInfluences = "maintainMaxInfluences"
    kWeights = "weights"
    kBindMatrix = 'bindMatrix'

    kShape = "shape"
    kShapeData = "shapeData"
    kShapeType = "shapeType"

    kApiType = OpenMaya.MFn.kSkinClusterFilter

    def __init__(self, node=None, **kwargs):
        super(Skin, self).__init__(node=node, **kwargs)

        self._shape_namespace = ""
        self._joint_namespace = ""

        self._influences_ids = list()
        self._influences_names = list()
        self._weights = OpenMaya.MDoubleArray()
        self._bind_matrix = list()

        self._skinning_method = 0
        self._use_components = False
        self._deform_user_normals = True
        self._dqs_support_non_rigid = False
        self._dqs_scale = [1.0, 1.0, 1.0]
        self._normalize_weights = 1
        self._weight_distribution = 0
        self._max_influences = 8
        self._maintain_max_influences = True
    
    @property
    def shape(self) -> str:
        return self._shape

    @property
    def shape_data(self) -> dict:
        return self._shape_data 

    def __repr__(self):
        return "{0}(name: {1}, shape: {2}, InfluencesCount: {3})".format(self.__class__.__name__,
                                                                         self.name,
                                                                         self._shape.name if self._shape else '',
                                                                         self.influence_count())

    def add_joint(self, name: str, pos: Union[list, OpenMaya.MVector, OpenMaya.MPoint]=None,
                  parent: Union[str, OpenMaya.MObject] = None, build: bool = False) -> OpenMaya.MObject:
        if build:
            name = cmds.createNode('joint', name=name, parent=parent)
        if pos:
            cmds.xform(name, translation=[pos[0], pos[1], pos[2]], worldSpace=True)
        cmds.skinCluster(self.name, edit=True, addInfluence=name, lockWeights=True, weight=0.0)

        return utils.get_object(name)

    def add_cluster_from_soft_selection(self, name: str, parent: str = None):
        """!@Brief Create new joint from soft selection."""
        if self.is_empty():
            raise RuntimeError('Current instance is empty !')

        soft_vertices = utils.soft_selection_weights()
        if not soft_vertices:
            return

        affected_influences = self.retrieve_influences_from_vertices([x.index for x in soft_vertices])

        new_joint = self.create_joint_from_soft_selection(soft_vertices, name, joint_parent=parent)
        self._get_data(self._object, get_weights=False)
        affected_influences.append(self._influences_ids[-1])
        weights = self.get_weights(influence_ids=affected_influences)

        self.lock_influences(False)
        influence_count = len(affected_influences)
        for soft_vertex in soft_vertices:
            for i in range(influence_count):
                j = soft_vertex.index * influence_count + i
                if i == influence_count - 1:
                    weight = soft_vertex.weight
                else:
                    weight = round(weights[j] - soft_vertex.weight * weights[j], 4)
                weights.set(weight, j)

        self._set_weights(weights=weights, influence_ids=affected_influences)

        return new_joint

    def apply(self, normalize: bool = False, weights: OpenMaya.MDoubleArray = None):
        if self.is_empty():
            raise Exception("Impossible to apply weights on empty instance.")

        return self._set_weights(normalize=normalize, weights=weights)
    
    def bind(self):
        if not self._shape:
            raise RuntimeError('No shape to attach skin !')
        if not self._influences_names:
            raise RuntimeError('No influences to attach skin !')
        
        skin = cmds.skinCluster(self._influences_names, self._shape.name, toSelectedBones=True, skinMethod=0)[0]
        self._object = utils.get_object(skin)

    def _clear(self):
        """!@Brief Clear instance."""

        self._shape = None
        self._shape_data = None

        self._shape_namespace = ""
        self._joint_namespace = ""

        self._influences_ids = list()
        self._influences_names = list()
        self._weights = list()

        self._skinning_method = 0
        self._use_components = False
        self._deform_user_normals = True
        self._dqs_support_non_rigid = False
        self._dqs_scale = [1.0, 1.0, 1.0]
        self._normalize_weights = 1
        self._weight_distribution = 0
        self._max_influences = 8
        self._maintain_max_influences = True

    def create_joint_from_soft_selection(self, soft_vertices: list, name: str, parent: str = None) -> OpenMaya.MObject:
        """!@Brief Create new joint from soft selection."""
        shape_name = utils.get_path(soft_vertices[0].name)
        shape = Node.get_node(shape_name)
        points = shape.points(shape, vertex_ids=[x.index for x in soft_vertices])
        pos = math.weighted_centroid(points, [x.weight for x in soft_vertices], weight_tolerence=0.75)

        return self.add_joint(name, pos=pos, joint_parent=parent, build=True)

    def from_dict(self, data: dict, shape_namespace: str = None,
                  joint_namespace: str = None, joint_root: Union[str, OpenMaya.MObject] = None):
        self._clear()
        self.__retrieve_shape(data)
        self.__set_data(data, shape_namespace, joint_namespace)
        self.__retrieve_influence_from_data(joint_root)
        self.__retrieve_skin_from_data(data)
        self.__retrieve_shape_from_data(data)

        return self

    def _get_data(self, node: Union[str, OpenMaya.MObject], get_weights: bool = True):
        super()._get_data(node)
        if not self.is_skin(node):
            raise TypeError(f"Node must be a SkinCluster not {self._object.apiTypeStr()} !")

        name = self.name
        self._skinning_method = cmds.getAttr('{0}.{1}'.format(name, self.kSkinningMethod))
        self._use_components = cmds.getAttr('{0}.{1}'.format(name, self.kUseComponents))
        self._deform_user_normals = cmds.getAttr('{0}.{1}'.format(name, self.kDeformUserNormals))
        self._dqs_support_non_rigid = cmds.getAttr('{0}.{1}'.format(name, self.kDqsSupportNonRigid))
        self._dqs_scale = cmds.getAttr('{0}.{1}'.format(name, self.kDqsScale))
        self._normalize_weights = cmds.getAttr('{0}.{1}'.format(name, self.kNormalizeWeights))
        self._weight_distribution = cmds.getAttr('{0}.{1}'.format(name, self.kWeightDistribution))
        self._max_influences = cmds.getAttr('{0}.{1}'.format(name, self.kMaxInfluences))
        self._maintain_max_influences = cmds.getAttr('{0}.{1}'.format(name, self.kMaintainMaxInfluences))
        self._bind_matrix = [cmds.getAttr('{0}.bindPreMatrix[{1}]'.format(name, i)) for i in range(self.influence_count())]
        self._influences_ids, self._influences_names = self._get_influences()
        if get_weights:
            self._weights = self.get_weights()
    
    def _get_influences(self) -> tuple:
        if not self._object:
            raise Exception("No SkinCluster setted")

        ids = list()
        influences = list()

        mfn = OpenMayaAnim.MFnSkinCluster(self._object)
        influences_paths = mfn.influenceObjects()
        for path in influences_paths:
            ids.append(mfn.indexForInfluenceObject(path))
            influences.append(path.fullPathName())

        return ids, influences

    def get_shape_component(self):
        if self._shape.has_fn(OpenMaya.MFn.kMesh):
            component = self._shape.component()
        else:
            raise RuntimeError(f"Invalide shape type {self._shape.apiTypeStr()} !")

        return component

    def get_weights(self, influence_ids: Union[int, list, tuple, OpenMaya.MIntArray] = None) -> OpenMaya.MDoubleArray:
        if self.is_empty():
            raise RuntimeError('Current instance is empty')

        component = self.get_shape_component()
        if influence_ids is None:
            influence_ids = OpenMaya.MIntArray(list(range(self.influence_count())))
        elif isinstance(influence_ids, (list, tuple)):
              influence_ids = OpenMaya.MIntArray(influence_ids)  

        mfn = OpenMayaAnim.MFnSkinCluster(self._object)
        return mfn.getWeights(self._shape.path,
                              component,
                              influence_ids)
    
    def influence_count(self) -> int:
        return len(self._influences_ids)

    def is_empty(self) -> bool:
        return self._object is None and self._shape is None and len(self._influences_ids) == 0 and \
               len(self._influences_names) == 0 and self._weights.length() == 0

    @classmethod
    def is_skin(cls, node: Union[str, OpenMaya.MObject]) -> bool:
        if isinstance(node, str):
            node = utils.get_object(node)

        return node.hasFn(OpenMaya.MFn.kSkinClusterFilter)

    def lock_influences(self, value: bool):
        skin_name = self.name
        [cmds.skinCluster(skin_name, edit=True, influence=x, lockWeights=value) for x in self._influences_names]
    
    @classmethod
    def read(cls, file_path: str, shape_namespace: str = None, joint_namespace: str = None, joint_root: str = None):
        if not os.path.exists(file_path):
            raise RuntimeError('Path "{0}" does not exists !'.format(file_path))
        
        try:
            with open(file_path, 'r') as stream:
                data = json.load(stream)
        except Exception:
            raise RuntimeError(f"Error on read skin data {file_path} !")
        
        new_cls = cls()
        new_cls.from_dict(data,
                          shape_namespace=shape_namespace,
                          joint_namespace=joint_namespace,
                          joint_root=joint_root)

        return new_cls

    def __retrieve_influence_from_data(self, joint_root):
        if not joint_root:
            if self._joints_namespace:
                for i, inf in enumerate(self._influences_names):
                    self._influences_names[i] = "{0}:{1}".format(self._joints_namespace, inf)
        else:
            if isinstance(joint_root, str):
                joint_root = utils.get_object(joint_root)
            if isinstance(joint_root, OpenMaya.MDagPath):
                joint_root = joint_root.node()

            root_name = utils.name(joint_root)
            children = cmds.listRelatives(root_name, allDescendents=True, fullPath=True, type='joint') or list()
            children.append(root_name)
            short_names = [child.split('|')[-1].split(':')[-1] for child in children]

            for i, inf in enumerate(self._influences_names):
                inf_count = short_names.count(inf)
                if inf_count == 0:
                    raise RuntimeError('Influence "{0}" not found'.format(inf))
                elif inf_count > 1:
                    raise RuntimeError('Multi node found with short name "{0}"'.format(inf))
                self._influences_names[i] = utils.name(children[short_names.index(inf)])

    def retrieve_influences_from_vertices(self, vertex_ids: list, tolerance: float = 1e-4) -> list:
        """!@Brief Retrieve all influences from given vertices."""
        if self.is_empty():
            raise RuntimeError('Current instance is empty !')

        influences = set()
        for vertex_id in vertex_ids:
            for inf_id in self._influences_ids:
                weight = self._weights[vertex_id * self.influence_count() + inf_id]
                if weight > tolerance:
                    influences.add(inf_id)

        return sorted(list(influences))

    def __retrieve_shape_from_data(self, data):
        shape_data = data.get(self.kShapeData, None)
        if not shape_data:
            raise RuntimeError('Missing shape data !')

        self._shape_data = shape_data
        shape_name = self._shape_data.get(self.kName, None)
        if shape_name:
            if self._shape_namespace:
                shape_name = "{0}:{1}".format(self._shape_namespace, shape_name)
            if cmds.objExists(shape_name) is True:
                self._shape = Node.get_node(shape_name)
            else:
                raise Exception('Shape "{0}" not found !'.format(shape_name))

    def __retrieve_skin_from_data(self, data):
        skin_name = data.get(self.kName, None)
        if skin_name:
            skin_name = "{0}:{1}".format(self._shape_namespace, skin_name)
            if cmds.objExists(skin_name):
                self._object = utils.get_object(skin_name)

    def __retrieve_shape(self, data: dict):
        shape = data.get(self.kShape, None)
        if not shape:
            return

        try:
            self._shape = Node.get_node(shape)
        except Exception:
            log.warning(f"Shape {shape} not found.")

    def __set_data(self, data: dict, shape_namespace: str, joint_namespace: str):

        self._shape_namespace = shape_namespace
        self._joints_namespace = joint_namespace
        self._skinning_method = data.get(self.kSkinningMethod, 0)
        self._use_components = data.get(self.kUseComponents, False)
        self._deform_user_normals = data.get(self, True)
        self._dqs_support_non_rigid = data.get(self, False)
        self._dqs_scale = data.get(self.kDqsScale, [1.0, 1.0, 1.0])
        self._normalize_weights = data.get(self.kNormalizeWeights, 1)
        self._weight_distribution = data.get(self, 0)
        self._max_influences = data.get(self.kMaxInfluences, 8)
        self._maintain_max_influences = data.get(self.kMaintainMaxInfluences, True)
        self._influences_ids = data.get(self.kInfluencesIDs, list())
        self._influences_names = cmds.ls(data.get(self.kInfluencesNames, list()), long=True)
        self._weights = OpenMaya.MDoubleArray(data.get(self.kWeights, list()))
        if not len(self._weights):
            raise RuntimeError('No weight data found !')

    def _set_weights(self, normalize: bool = False,
                     weights: OpenMaya.MDoubleArray = None,
                     influence_ids: Union[int, list, tuple, OpenMaya.MIntArray] = None) -> OpenMaya.MDoubleArray:
        """!@Brief Set SkinCluster weight from MOPSkinTools instance."""
        if not self._object:
            raise Exception("No SkinCluster setted.")

        component = self._shape.components()
        if weights is not None:
            self._weights = weights

        if influence_ids is None:
            influences_ids = OpenMaya.MIntArray(list(range(self.influence_count())))
        elif isinstance(influence_ids, (list, tuple)):
              influences_ids = OpenMaya.MIntArray(influence_ids)  

        mfn = OpenMayaAnim.MFnSkinCluster(self._object)
        return mfn.setWeights(self._shape.path,
                              component,
                              influences_ids,
                              self._weights,
                              normalize, returnOldWeights=True)

    @classmethod
    def find(cls, node: Union[str, OpenMaya.MObject]) -> OpenMaya.MObject:
        """!@Brief Find skin cluster from given node."""
        return Deformer._find(node, cls.kApiType)

    @classmethod
    def get(cls, node: Union[str, OpenMaya.MObject, OpenMaya.MDagPath]) -> "Skin":
        node = cls.find(node)
        return cls(node) if node else None

    def to_dict(self) -> dict:
        if self.is_empty():
            raise Exception("Data of this instance is empty !")

        self._get_data(self._object, get_weights=True)

        data = {self.kName: utils.name(self._object, False, False),
                self.kShape: self._shape.name,
                self.kSkinningMethod: self._skinning_method, self.kUseComponents: self._use_components,
                self.kDeformUserNormals: self._deform_user_normals,
                self.kDqsSupportNonRigid: self._dqs_support_non_rigid, self.kDqsScale: self._dqs_scale,
                self.kNormalizeWeights: self._normalize_weights, self.kWeightDistribution: self._weight_distribution,
                self.kMaxInfluences: self._max_influences, self.kMaintainMaxInfluences: self._maintain_max_influences,
                self.kInfluencesIDs: self._influences_ids,
                self.kInfluencesNames: [x.split("|")[-1].split(":")[-1] for x in self._influences_names],
                self.kWeights: list(self._weights),
                self.kShapeData: self._shape.to_dict(),
                self.kBindMatrix: self._bind_matrix}

        return data
