from __future__ import annotations
import os
import json
from typing import Union

from maya import cmds
from maya.api import OpenMaya, OpenMayaAnim

from HodoRig.Core import utils
from HodoRig.Core.logger import log
from HodoRig.Core.Deformers.deformer import Deformer
from HodoRig.Nodes.node import Node

from qdHelpers import qdAttr
from qdHelpers.mayaProgressBar import ProgressBar


class BlendShape(Deformer):

    kType = 'blendShape'
    kApiType = OpenMaya.MFn.kBlendShape

    kShape = 'shape'
    kDeformer = 'deformer'
    kTarget = 'target'
    kName = 'name'
    kIndex = 'index'
    kVertices = 'vertices'
    kWeights = 'weights'
    kOffsets = 'offsets'

    def __init__(self, node=None):
        super(BlendShape, self).__init__(node=node)

        self._mfn = None
        if node:
            self.__get(node)

    def __call__(self, mo_node=None, **kwargs):

        super(BlendShape, self).__call__(mo_node=mo_node, **kwargs)

        self._mfn = None
        if mo_node:
            self.__get(mo_node)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return "{0}({1})".format(self.__class__.__name__, self.name)

    @classmethod
    def create(cls, mo_shape, s_name, d_data=None):

        """
        !@Brief Create new deformer.

        @type mo_shape: OpenMaya.MObject
        @param mo_shape: Source shape.
        @type s_name: str / unicode
        @param s_name: Deformer name
        @type d_data: dict
        @param d_data: BlendShape data.

        @rtype: OpenMaya.MObject
        @return: Deformer object.
        """

        mo_deformer = cls._create(mo_shape, cls.kType, s_name)
        if d_data:
            cls.log.error('Apply data no implemented yet !')
        return BlendShape(mo_deformer)

    def __get(self, node):

        """
        !@Brief Get MFnBlendShapeDeformer from given name.
            If node given is Mesh / NurbsCurve / NurbsSurface parse history

        @type node: str / unicode / OpenMaya.MObject
        @param: node: BlendShape object.
        """

        if isinstance(node, str):
            node = utils.get_object(node)
        elif isinstance(node, OpenMaya.MObject) is False:
            s_msg = "Argument musst be a MObject not {0}".format(type(node))
            self.log.error(s_msg)
            raise TypeError(s_msg)

        if node.hasFn(OpenMaya.MFn.kBlendShape) is False:
            s_msg = 'Node must be a BlendShape not "{0}"'.format(node.apiTypeStr())
            self.log.error(s_msg)
            raise RuntimeError(s_msg)

        self._mfn = OpenMayaAnim.MFnBlendShapeDeformer(node)

    # =========================================
    #    Accesseur
    # =========================================

    @classmethod
    def find(cls, mo_node):

        """
        !@Brief Find Blendshape from given node.

        @type mo_node: str / unicode / OpenMaya.MObject
        @param mo_node: Shape object. If transform is given get shape first

        @rtype: OpenMaya.MObject
        @return: SkinCluster object.
        """

        return QDDeformer._find(mo_node, cls.kApiType)

    @property
    def object(self):
        """
        !@Brief Get object.
        """
        return self._mo_object

    @object.setter
    def object(self, value):

        """
        !@Brief Set new object.

        @type value: OpenMaya.MObject
        @param value: New object.
        """

        if isinstance(value, OpenMaya.MObject) is False:
            s_msg = "Argument must be a MObject not {0}".format(type(value))
            self.log.error(s_msg)
            raise RuntimeError(s_msg)

        if value.hasFn(OpenMaya.MFn.kBlendShape) is False:
            s_msg = "Node must be a blendShape not {0}".format(value.apiTypeStr())
            self.log.error(s_msg)
            raise RuntimeError(s_msg)

        self._mo_object = value
        self._s_name = OpenMaya.MFnDependencyNode(value).name()
        self._mfn = OpenMayaAnim.MFnBlendShapeDeformer(value)

    def mfn_node(self):
        """
        !@Brief Get blendshape container.

        @rtype: MFnBlendShapeDeformer
        @return: Blendshape.
        """
        return OpenMayaAnim.MFnBlendShapeDeformer(self.object)

    def count(self):

        """
        !@Brief Get target count and force evaluation of count.

        @rtype: int
        @return: Blendshape target count.
        """

        return self.get_weight_plug().numElements()

    def get_enveloppe_plug(self):

        """
        !@Brief Get deformer envelope plug

        @rtype: OpenMaya.MPlug
        @return: Envelope plug.
        """

        return qdAttr.retrieve(self.object, self.kEnvelope)

    def get_weight_plug(self):

        """
        !@Brief Get master target weight plug.

        @rtype: OpenMaya.MPlug
        @return: Weight plug.
        """

        return qdAttr.retrieve(self.object, self.kWeight)

    def get_weight_plugs(self):

        """
        !@Brief Get all weight plugs of this blendshape.

        @rtype: OpenMaya.MPlugArray
        @return: Array of blendshape weight plugs.
        """

        mp_weights = self.get_weight_plug()
        mpa_weights = OpenMaya.MPlugArray()
        for idx in range(mp_weights.numElements()):
            mp = mp_weights.elementByLogicalIndex(idx)
            if mp.isNull():
                continue
            mpa_weights.append(mp)

        return mpa_weights

    def get_weight_indices(self):

        """
        !@Brief Get Blendshape weight index.

        @rtype: OpenMaya.MIntArray
        @return: Array of weight indices.
        """

        mpa_weights = self.get_weight_plugs()
        mia_index = OpenMaya.MIntArray(mpa_weights.length(), 0)
        for i in range(mpa_weights.length()):
            mia_index.set(mpa_weights[i].logicalIndex(), i)

        return mia_index

    def get_weight_alias(self):

        """
        !@Brief Get all target weight alias of blendshape.

        @rtype: list(string)
        @return: List of attribute alias.
        """

        mpa_weights = self.get_weight_plugs()
        a_alias = list()
        for i in range(mpa_weights.length()):
            mfn = OpenMaya.MFnDependencyNode(mpa_weights[i].node())
            a_alias.append(mfn.plugsAlias(mpa_weights[i]))

        return a_alias

    def get_weights(self):

        """
        !@Brief Get all weight value of blendshape.

        @rtype: list(float)
        @return: List of weight values.
        """

        mpa_weights = self.get_weight_plugs()
        mfa_value = OpenMaya.MDoubleArray(mpa_weights.length(), 0.0)
        for i in range(mpa_weights.length()):
            mfa_value.set(mpa_weights[i].asFloat(), i)

        return mfa_value

    def get_target_group_plug(self, i_target_id, i_input_id=0):

        """
        !@Brief Get target group plug.

        @type i_target_id: int
        @param i_target_id: Target index.
        @type i_input_id: int
        @param i_input_id: Input shape index.

        @rtype: OpenMaya.MPlug
        @return: Target group plug.
        """

        mp_target = qdAttr.retrieve(self.object, self.kInputTarget)
        return mp_target.elementByLogicalIndex(i_input_id).child(0).elementByLogicalIndex(i_target_id)

    def get_target_item_plug(self, i_target_id, i_input_id=0):

        """
        !@Brief Get target item plug at given index.

        @type i_target_id: int
        @param i_target_id: Target index.
        @type i_input_id: int
        @param i_input_id: Input shape index.

        @rtype: OpenMaya.MPlug
        @return: Target item plug.
        """

        return self.get_target_group_plug(i_target_id, i_input_id).child(0)

    def get_target_geometry_plug(self, i_target_id, i_input_id=0, i_weight_id=6000):

        """
        !@Brief Get target geometry plug at given index.

        @type i_target_id: int
        @param i_target_id: Target index.
        @type i_input_id: int
        @param i_input_id: Input shape index.
        @type i_weight_id: int
        @param i_weight_id: Weight value, see doc for get good value. Default value for weight at 1.0 is 6000.

        @rtype: OpenMaya.MPlug
        @return: Target geometry plug.
        """

        return self.get_target_item_plug(i_target_id, i_input_id=i_input_id).elementByLogicalIndex(i_weight_id).child(0)

    def get_target_shape(self, i_target_id, i_input_id=0, i_weight_id=None):

        """
        !@Brief Get target shape from given index.

        @type i_target_id: int
        @param i_target_id: Target index.
        @type i_input_id: int
        @param i_input_id: Input shape index.
        @type i_weight_id: int
        @param i_weight_id: Weight value, see doc for get good value. Default value for weight at 1.0 is 6000.

        @rtype: OpenMaya.MObject
        @return: Target shape object.
        """

        mp_target_geometry = self.get_target_geometry_plug(i_target_id, i_input_id=i_input_id, i_weight_id=i_weight_id)
        mp_input = mp_target_geometry.source()
        return None if mp_input.isNull() else mp_input.node()

    def get_target_weight_plug(self, i_target_id, i_input_id=0):

        """
        !@Brief Get target weight plug.

        @type i_target_id: int
        @param i_target_id: Target index.
        @type i_input_id: int
        @param i_input_id: Input shape index.

        @rtype: OpenMaya.MPlug
        @return: Target weight plug.
        """

        #   Get input target
        return self.get_target_group_plug(i_target_id, i_input_id).child(1)

    def get_target_weights(self, i_target_id, i_input_id=0):

        """
        !@Brief Get target weights values.

        @type i_target_id: int
        @param i_target_id: Target index.
        @type i_input_id: int
        @param i_input_id: Input shape index.

        @rtype: list
        @return: Target weights.
        """

        return qdAttr.get(self.get_target_weight_plug(i_target_id, i_input_id=i_input_id))

    def get_target_offset_plug(self, i_target_id, i_input_id=0, i_weight_id=6000):

        """
        !@Brief Get target point offset plug.

        @type i_target_id: int
        @param i_target_id: Target index.
        @type i_input_id: int
        @param i_input_id: Input shape index.
        @type i_weight_id: int
        @param i_weight_id: Weight value, see doc for get good value. Default value for weight at 1.0 is 6000.

        @rtype: OpenMaya.MPlug
        @return: Attribute.
        """

        return self.get_target_item_plug(i_target_id, i_input_id=i_input_id).elementByLogicalIndex(i_weight_id).child(3)

    def get_target_component_plug(self, i_target_id, i_input_id=0, i_weight_id=6000):

        """
        !@Brief Get target component plug.

        @type i_target_id: int
        @param i_target_id: Target index.
        @type i_input_id: int
        @param i_input_id: Input shape index.
        @type i_weight_id: int
        @param i_weight_id: Weight value, see doc for get good value. Default value for weight at 1.0 is 6000.

        @rtype: OpenMaya.MPlug
        @return: Attribute.
        """

        return self.get_target_item_plug(i_target_id, i_input_id=i_input_id).elementByLogicalIndex(i_weight_id).child(4)

    def get_target_offset(self, i_target_id, i_input_id=0, i_weight_id=6000):
        """
        !@Brief Get target point offset
        @type i_target_id: int
        @param i_target_id: Target index.
        @type i_input_id: int
        @param i_input_id: Input shape index.
        @type i_weight_id: int
        @param i_weight_id: Weight value, see doc for get good value. Default value for weight at 1.0 is 6000.
        @rtype: OpenMaya.MPointArray
        @return: List of point offset
        """
        mpa_offsets = OpenMaya.MPointArray()
        #   Refresh target
        self.refresh_target(i_target_id, i_input_id, i_weight_id)
        #   Get offsets
        mp_item_offset = self.get_target_offset_plug(i_target_id, i_input_id=i_input_id, i_weight_id=i_weight_id)
        if mp_item_offset.isDefaultValue():
            return mpa_offsets
        OpenMaya.MFnPointArrayData(mp_item_offset.asMObject()).copyTo(mpa_offsets)
        return mpa_offsets

    def get_index_by_name(self, s_name):

        """
        !@Brief Get Index of target by name.

        @type s_name: string
        @param s_name: Name of target

        @rtype: int
        @return: Index of target
        """

        return self.get_weight_indices()[self.get_weight_alias().index(s_name)]

    def get_target_data(self, i_target_id, i_input_id=0):

        """
        !@Biref Get target data

        @type i_target_id: int
        @param i_target_id: target index
        @type i_input_id: int
        @param i_input_id: index of input shape

        @rtype: dict
        @return: Target data.
        """

        self.refresh_target(i_target_id, i_input_id=i_input_id)

        #   Get components index
        a_components = self.get_components_indices(i_target_id)
        if len(a_components) == 0:
            mo_target = self.get_target_shape(i_target_id, i_input_id=i_input_id)
            a_components = [i for i in range(OpenMaya.MFnMesh(mo_target).numVertices())]

        #   Init data
        d_data = dict()
        d_data[self.kName] = self.get_weight_alias()[i_target_id]
        d_data[self.kIndex] = i_target_id
        d_data[self.kVertices] = a_components
        d_data[self.kWeights] = self.get_target_weights(i_target_id, i_input_id=i_input_id)
        mpa = self.get_target_offset(i_target_id, i_input_id=i_input_id)
        d_data[self.kOffsets] = [(mpa[i].x, mpa[i].y, mpa[i].z) for i in range(mpa.length())]

        return d_data

    def get_components_datas(self, i_target_id, i_input_id=0):

        """
        !@Biref Get components datas of target weight datas

        @type i_target_id: int
        @param i_target_id: Target index.
        @type i_input_id: int
        @param i_input_id: Input shape index.

        @rtype: OpenMaya.MFnSingleIndexedComponent
        @return: MFnSingleIndexedComponent.
        """

        #    Get plug of input components
        mp_input_target = qdAttr.retrieve(self.object, self.kInputTarget)
        mp_target_group = mp_input_target[i_input_id].child(0)
        mp_target_item = mp_target_group[i_target_id].child(0)

        #   Get num target. Force get count with evaluateNumElements.
        mp_target_item.evaluateNumElements()
        i_count = mp_target_item.numElements()

        #   Check Connection. If target is connected, diconnect for force refresh components list.
        mp_target_geom = mp_target_item[i_count - 1].child(0)
        mp_source_geom = mp_target_geom.source()
        if mp_source_geom.isNull() is False:
            self.log.debug('Disconnect "{0}" to "{1}"'.format(mp_source_geom.name(), mp_target_geom.name()))
            qdAttr.disconnect(mp_source_geom, mp_target_geom)

        #   Get components datas.
        #   New attribute index change with Maya 2018
        #   Components object is in position 4 now.
        mp_component_target_plug = mp_target_item[i_count - 1].child(4)
        if mp_component_target_plug.isDefaultValue():
            return None
        mo_component_target = mp_component_target_plug.asMObject()
        mfn_data = OpenMaya.MFnComponentListData(mo_component_target)

        #   If target is connected before get compoenents datas, reconnect source on target plug.
        if mp_source_geom.isNull() is False:
            self.log.debug('Reconnect "{0}" to "{1}"'.format(mp_source_geom.name(), mp_target_geom.name()))
            qdAttr.connect(mp_source_geom, mp_target_geom)

        return mfn_data

    def get_components_indices(self, i_target_id, i_input_id=0):

        """
        !@Biref Transform ComponentWeightDatas to MIntArray.

        @type i_target_id: int
        @param i_target_id: Target index.
        @type i_input_id: int
        @param i_input_id: Input shape index.

        @rtype: list
        @return: List of deformed components.
        """

        a_indices = list()

        #    Get components datas
        mfn_datas = self.get_components_datas(i_target_id, i_input_id=i_input_id)
        if mfn_datas is None:
            return a_indices

        #    Transform to list of int
        a_indices = list()
        for i in range(mfn_datas.length()):
            input_components = OpenMaya.MFnSingleIndexedComponent(mfn_datas[i])
            if input_components.isEmpty():
                continue
            mia_current_indices = OpenMaya.MIntArray()
            input_components.getElements(mia_current_indices)
            for j in range(mia_current_indices.length()):
                a_indices.append(mia_current_indices[j])

        return a_indices

    # =========================================
    #    Misc
    # =========================================

    def extract_target(self, i_target_id, i_input_id=0, i_weight_id=6000, connect_target=True, f_epsilon=1e-6):

        """
        !@Brief Extract from base baseObject and Offset point.

        @type i_target_id: int
        @param i_target_id: Target index
        @type i_input_id: int
        @param i_input_id: Input shape index.
        @type i_weight_id: int
        @param i_weight_id: Weight value, see doc for get good value. Default value for weight at 1.0 is 6000.
        @type connect_target: bool
        @param connect_target: Connect new node to target geometry plug.
        @type f_epsilon: float
        @param f_epsilon: Offset tolerence.

        @rtype: OpenMaya.MDagPath
        @return: DagPath of new node.
        """

        mo_orig = self.inputs_geometry()[i_input_id]
        if mo_orig.hasFn(OpenMaya.MFn.kMesh) is False:
            s_msg = 'Only mesh blendShape is implemented  not "{0}" !'.format(mo_orig.apiTypeStr())
            self.log.error(s_msg)
            raise RuntimeError(s_msg)

        #   Duplicate baseObject
        mo_shape = self.duplicate_orig(self.get_weight_alias()[i_target_id])

        #   Get points datas
        mpa_offset = self.get_target_offset(i_target_id, i_input_id=i_input_id, i_weight_id=i_weight_id)
        mid_indices = self.get_components_indices(i_target_id, i_input_id=i_input_id)

        #   Set Points
        mpa_points = OpenMaya.MPointArray()
        mfn_mesh = OpenMaya.MFnMesh(mo_shape)
        mfn_mesh.getPoints(mpa_points, OpenMaya.MSpace.kObject)
        m_pb = ProgressBar(mpa_offset.length(), "Set Points Offset")
        for i in range(mpa_offset.length()):
            mv = OpenMaya.MVector(mpa_offset[i])
            if mv.length() < f_epsilon:
                continue
            mpa_points.set(mpa_points[mid_indices[i]] + mv, mid_indices[i])
            m_pb.update(i)
        m_pb.kill()
        mfn_mesh.setPoints(mpa_points, OpenMaya.MSpace.kObject)

        #   Connect target
        if connect_target:
            world_mesh_plug = qdAttr.retrieve(mo_shape, self.kWorldMesh).elementByLogicalIndex(0)
            mp_target_geom = self.get_target_geometry_plug(i_target_id, i_input_id=i_input_id, i_weight_id=i_weight_id)
            qdAttr.connect(world_mesh_plug, mp_target_geom)

        return mo_shape

    def add_target(self, mo_shape, i_input_id=0, weight=1.0):

        """
        !@Brief Add new target to blendShape deformer.

        @type mo_shape: OpenMaya.MObject
        @param mo_shape: Shape node you want to add
        @type i_input_id: int
        @param i_input_id: Input shape index.
        @type weight: float
        @param weight: Weight of target. By default is 1.0. If you give other float it's a inBetween target
        """

        #   Get base object
        base_objects = self.outputs_geometry()

        #   Check nodes
        if isinstance(mo_shape, str):
            mo_shape = utils.get_object(mo_shape)

        if isinstance(mo_shape, OpenMaya.MObject) is False:
            s_msg = 'Argument must be MObject not "{0}" !'.format(mo_shape.apiTypeStr())
            self.log.error(s_msg)
            raise RuntimeError(s_msg)

        if mo_shape.hasFn(OpenMaya.MFn.kShape) is False:
            dp = OpenMaya.MDagPath()
            OpenMaya.MDagPath().getAPathTo(mo_shape, dp)
            dp.extendToShape()
            mo_shape = dp.node()

        if mo_shape.hasFn(OpenMaya.MFn.kMesh) is False:
            s_msg = 'New target must be a mesh not "{0}" !'.format(mo_shape.apiTypeStr())
            self.log.error(s_msg)
            raise RuntimeError(s_msg)

        # Add target
        i_target_id = qdAttr.get_first_free(self.get_weight_plug()).logicalIndex()
        s_name = utils.name(OpenMaya.MFnDagNode(mo_shape).parent(0), b_full=False, b_namespace=False)
        self._mfn.addTarget(base_objects[i_input_id], i_target_id, mo_shape, weight)
        self.rename_weight_alias(i_target_id, s_name)

    def remove_target(self, i_target_id, i_input_id=0, i_weight_id=None, weight=1.0):

        """
        !@Brief Remove target to blendShape node

        @type i_target_id: int
        @param i_target_id: Target index
        @type i_input_id: int
        @param i_input_id: Input shape index.
        @type i_weight_id: int
        @param i_weight_id: Weight of target. By default is 1.0. If you give other float it's a inBetween target
        @type weight: float
        @param weight: Weight of target. Default is 1.0
        """

        mo_shape = self.outputs_geometry()[i_input_id]

        #   Check target geometry plug connection. If plug not have connection create it with base object.
        mp_target_geom = self.get_target_geometry_plug(i_target_id, i_input_id=i_input_id, i_weight_id=i_weight_id)
        mp_source = mp_target_geom.source()

        if mp_source.isNull():
            mo_input = self.duplicate_shape('bs_tmp_remove')
            qdAttr.connect(qdAttr.retrieve(mo_input, self.kWorldMesh).elementByLogicalIndex(0), mp_target_geom)
        else:
            mo_input = mp_source.node()

        #   Remove target
        self._mfn.removeTarget(mo_shape, i_target_id, mo_input, weight)

    def replace_target(self, mo_shape, i_target_id, i_input_id=0, i_weight_id=None):

        """
        !@Brief Replace target of blendshape.

        @type mo_shape: OpenMaya.MObject
        @param mo_shape: New target node.
        @type i_target_id: int
        @param i_target_id: Target index.
        @type i_input_id: int
        @param i_input_id: Input shape index.
        @type i_weight_id: int
        @param i_weight_id: Weight value, see doc for get good value. Default value for weight at 1.0 is 6000.
        """

        #   Check nodes
        if isinstance(mo_shape, str):
            mo_shape = utils.get_object(mo_shape)

        if mo_shape.hasFn(OpenMaya.MFn.kShape) is False:
            dp = OpenMaya.MDagPath()
            OpenMaya.MDagPath().getAPathTo(mo_shape, dp)
            dp.extendToShape()
            if dp.isValid() is False:
                s_msg = 'No shape found on "{0}"'.format(utils.name(mo_shape))
                self.log.error(s_msg)
                raise RuntimeError(s_msg)
            mo_shape = dp.node()

        if mo_shape.hasFn(OpenMaya.MFn.kMesh) is False:
            s_msg = 'New target must be a mesh not "{0}"'.format(mo_shape.apiTypeStr())
            self.log.error(s_msg)
            raise RuntimeError(s_msg)

        #   Replace target geometry
        mp_target_geom = self.get_target_geometry_plug(i_target_id, i_input_id, i_weight_id)
        qdAttr.connect(qdAttr.retrieve(mo_shape, self.kWorldMesh).elementByLogicalIndex(0), mp_target_geom)
        s_name = utils.name(OpenMaya.MFnDagNode(mo_shape).parent(0), b_full=False, b_namespace=False)
        self.rename_weight_alias(i_target_id, s_name)

    def refresh_target(self, i_target_id, i_input_id=0, i_weight_id=6000):

        """
        !@Brief Refresh target datas. Disconnect target geometry and reconnect if plug is connected

        @type i_target_id: int
        @param i_target_id: Target index.
        @type i_input_id: int
        @param i_input_id: Input shape index.
        @type i_weight_id: int
        @type i_weight_id: Inbetween index.
        """

        mp_target_geom = self.get_target_geometry_plug(i_target_id, i_input_id=i_input_id, i_weight_id=i_weight_id)
        mp_source = mp_target_geom.source()
        if mp_source.isNull():
            return

        qdAttr.disconnect(mp_source, mp_target_geom)
        qdAttr.connect(mp_source, mp_target_geom)

    def refresh_target_weight(self, i_target_id, i_input_id=0, i_weight_id=6000):

        """
        !@Brief Refresh target datas. Disconnect target geometry and reconnect if plug is connected

        @type i_target_id: int
        @param i_target_id: Target index.
        @type i_input_id: int
        @param i_input_id: Input shape index.
        @type i_weight_id: int
        @type i_weight_id: Inbetween index.
        """

        # Force target refresh
        self.refresh_target(i_target_id, i_input_id=i_input_id, i_weight_id=i_weight_id)
        # Retrieve data
        mpa_offset = self.get_target_offset(i_target_id)
        mp_target_weight = self.get_target_weight_plug(i_target_id)
        a_components = self.get_components_indices(i_target_id)
        # Reset target weights
        vtx_count = OpenMaya.MFnMesh(self.outputs_geometry()[i_input_id]).numVertices()
        for i in range(vtx_count):
            qdAttr.set(mp_target_weight.elementByLogicalIndex(i), 0.0)
        # Normalisation des weights
        a_weight = list()
        for i in range(mpa_offset.length()):
            a_weight.append(round(OpenMaya.MVector(mpa_offset[i]).length(), 3))
        f_max = max(a_weight)
        # Apply des weights
        for i in range(mpa_offset.length()):
            qdAttr.set(mp_target_weight.elementByLogicalIndex(a_components[i]), a_weight[i] / f_max)

    def rename_weight_alias(self, i_target_id, s_name):

        """
        !@Brief Set weight plug alias.

        @type i_target_id: int
        @param i_target_id: Index of weight target you want to set.
        @type s_name: string
        @param s_name: New alias name.
        """

        # if i_target_id > self.count():
        #     s_msg = 'Invalid index given'
        #     self.log.error(s_msg)
        #     raise RuntimeError(s_msg)

        mp_weights = self.get_weight_plug()
        s_weight = mp_weights.elementByLogicalIndex(i_target_id).name().split('.')[-1]
        self._mfn.setAlias(s_name, s_weight, mp_weights, True)

    def reset_mesh(self, mo_shape, i_input_id=0):

        """
        !@Brief Reset one mesh to initial points with input blendshape geometry.

        @type mo_shape: OpenMaya.MObject
        @param mo_shape: Node you want to reset.
        @type i_input_id: int
        @param i_input_id: input blendshape index.
        """

        #   Get Orig
        mfn_orig = OpenMaya.MFnMesh(self.inputs_geometry()[i_input_id])
        mpa_points = OpenMaya.MPointArray()
        mfn_orig.getPoints(mpa_points, OpenMaya.MSpace.kObject)

        #   Set points
        if isinstance(mo_shape, OpenMaya.MObject) is False:
            s_msg = 'Argument must be a MObject not "{0}" !'.format(type(mo_shape))
            self.log.error(s_msg)
            raise RuntimeError(s_msg)

        mfn_target = OpenMaya.MFnMesh(mo_shape)
        mfn_target.setPoints(mpa_points)

        return self

    def restore_weights(self, d_data, i_target_id, i_input_id=0):

        """
        !@Biref Restore weight of blendshape target.

        @type d_data: dict
        @param d_data: Target data.
        @type i_target_id: int
        @param i_target_id: Target ID.
        @type i_input_id: int
        @param i_input_id: input blendshape index.
        """

        #   Set array
        a_weights = d_data[self.kWeights]
        a_vertices = d_data[self.kVertices]
        mfa = OpenMaya.MFloatArray(OpenMaya.MFnMesh(self.inputs_geometry()[i_input_id]).numVertices(), 0.0)
        for i in range(len(a_weights)):
            mfa.set(a_weights[i], a_vertices[i])

        mfn_array = OpenMaya.MFnFloatArrayData()
        mo_array = mfn_array.create()
        mfn_array.set(mfa)
        self.get_target_weight_plug(i_target_id, i_input_id=i_input_id).setMObject(mo_array)
        self.log.debug('Target "{0}" was updated.'.format(i_target_id))

    def extract_meshes(self, i_input_id=0, i_weight_id=6000, f_epsilon=1e-6):

        """
        !@Brief Extract all target of blendShape node

        @type i_input_id: int
        @param i_input_id: input blendshape index.
        @type i_weight_id: int
        @param i_weight_id: Weight value, see doc for get good value. Default value for weight at 1.0 is 6000.
        @type f_epsilon: float
        @param f_epsilon: Offset tolerence.

        @rtype: list(OpenMaya.MDagPath)
        @return: List of target extracted.
        """

        a_indices = self.get_weight_indices()
        moa_targets = OpenMaya.MObjectArray(len(a_indices))
        for i in range(len(a_indices)):
            target = self.extract_target(a_indices[i],
                                         i_input_id=i_input_id, i_weight_id=i_weight_id, f_epsilon=f_epsilon)
            moa_targets.set(target, i)

        return moa_targets

    def to_dict(self, i_target_id=0):

        """
        !@Brief Transform blendshape data to list.

        @type i_target_id: int
        @param i_target_id: Blendshape target id.

        @rtype: list
        @return: List of target data.
        """

        moa_outputs_geom = self.outputs_geometry()
        if moa_outputs_geom.length() == 0:
            s_msg = 'No output geometry found for "{0}"!'.format(self.name)
            self.log.error(s_msg)
            raise RuntimeError(s_msg)
        elif moa_outputs_geom.length() > 1:
            s_msg = 'Multi output geometry not implemented yet !'
            self.log.error(s_msg)
            raise RuntimeError(s_msg)

        d_data = dict()
        d_data[self.kShape] = utils.name(moa_outputs_geom[i_target_id])
        d_data[self.kName] = self.name
        d_data[self.kTarget] = list()

        a_indices = self.get_weight_indices()
        for i in range(len(a_indices)):
            d_data[self.kTarget].append(self.get_target_data(a_indices[i]))

        return d_data

    @classmethod
    def apply(cls, d_data, s_mesh_ns=None):

        """
        !@Brief Apply target from file.

        @type d_data: dict
        @param d_data: Blendshape data.
        @type s_mesh_ns: str / unicode
        @param s_mesh_ns: Mesh namesapce. Default is None

        @rtype: BlendShape
        @return: new blendshape instance
        """

        s_shape = d_data.get(cls.kShape, None)
        if s_shape is None:
            raise RuntimeError('No shape found on data !')

        s_current_namespace = OpenMaya.MNamespace.currentNamespace()
        if s_mesh_ns:
            s_shape = '{0}:{1}'.format(s_mesh_ns, s_shape.split('|')[-1].split(':')[-1])
            a_shape = cmds.ls(s_shape, long=True)
            if len(a_shape) > 1:
                raise RuntimeError('Multi shape found {0}'.format('\n\t'.join(a_shape)))
            # Set namespace
            if not OpenMaya.MNamespace.namespaceExists(s_mesh_ns):
                OpenMaya.MNamespace.setCurrentNamespace(OpenMaya.MNamespace.rootNamespace())
                OpenMaya.MNamespace.addNamespace(s_mesh_ns)
            OpenMaya.MNamespace.setCurrentNamespace(s_mesh_ns)
        else:
            s_shape = OpenMaya.MNamespace.stripNamespaceFromName(s_shape)

        s_name = d_data.get(cls.kName, 'blendShape1')
        bs = BlendShape.create(utils.get_object(s_shape), s_name)

        i_target_count = len(d_data[cls.kTarget])
        for i in range(i_target_count):
            d_target = d_data[cls.kTarget][i]
            i_index = d_target[cls.kIndex]
            a_vtx = d_target[cls.kVertices]
            a_off = d_target[cls.kOffsets]
            s_target_name = d_target[cls.kName]

            mia_vtx = OpenMaya.MIntArray(len(a_vtx), 0)
            [mia_vtx.set(a_vtx[i], i) for i in range(len(a_vtx))]
            mfn_vtx_comp = OpenMaya.MFnSingleIndexedComponent()
            mo_vtx = mfn_vtx_comp.create(OpenMaya.MFn.kMeshVertComponent)
            mfn_vtx_comp.addElements(mia_vtx)
            mfn_comp = OpenMaya.MFnComponentListData()
            mo_comp = mfn_comp.create()
            mfn_comp.add(mo_vtx)
            mp_item_component = bs.get_target_component_plug(i_index)
            mp_item_component.name()
            mp_item_component.setMObject(mo_comp)

            mpa_off = OpenMaya.MPointArray(len(a_off))
            [mpa_off.set(OpenMaya.MPoint(a_off[i][0], a_off[i][1], a_off[i][2]), i) for i in range(len(a_off))]
            mfn_off_data = OpenMaya.MFnPointArrayData()
            mo_off = mfn_off_data.create(mpa_off)
            mp_item_offset = bs.get_target_offset_plug(i_index)
            mp_item_offset.setMObject(mo_off)

            mp_weights = bs.get_weight_plug()
            mp_weight = mp_weights.elementByLogicalIndex(i_index)
            mp_weight.setFloat(0.0)
            mfn_attr = OpenMaya.MFnAttribute(mp_weight.attribute())
            mfn_attr.setHidden(False)
            bs.rename_weight_alias(i_index, s_target_name)

        if s_mesh_ns:
            OpenMaya.MNamespace.setCurrentNamespace(s_current_namespace)

        return bs

    @classmethod
    def apply_all(cls, s_file_path, s_mesh_ns=None):

        """
        !@Brief

        @type s_file_path: str / unicode
        @param s_file_path: File path.
        @type s_mesh_ns: str / unicode
        @param s_mesh_ns: Mesh namesapce. Default is None
        """

        if os.path.isfile(s_file_path) is False:
            s_msg = "Invalid path given -- {0}".format(s_file_path)
            cls.log.error(s_msg)
            raise TypeError(s_msg)

        with open(s_file_path, "r") as file_data:
            a_data = json.load(file_data)

        for d_data in a_data:
            try:
                BlendShape().apply(d_data, s_mesh_ns=s_mesh_ns)
            except Exception as e:
                s_msg = '{0}\nImpossible to apply Blendshape on "{1}"'.format(e, d_data.get("shape", "NO SHAPE FOUND"))
                cls.log.error(s_msg)
                continue

    @classmethod
    def _dump(cls, a_data, s_file_path):

        """
        !@Brief Dump data to file.

        @type a_data: list / tuple / dict
        @param a_data: Data.
        @type s_file_path: str / unicode
        @param s_file_path: File path.
        """

        s_dir, s_file = os.path.split(s_file_path)
        if os.path.exists(s_dir) is False:
            os.makedirs(s_dir)

        #   Write
        with open(s_file_path, 'w') as out_file:
            out_file.write(json.dumps(a_data, indent=0))

        cls.log.debug('BlendShape data write in to "{0}"'.format(s_file_path))

    @classmethod
    def read(cls, s_file_path):

        """
        !@Brief Read data from file.

        @type s_file_path: str / unicode
        @param s_file_path: File path.

        @rtype: list
        @return: Blendshape data.
        """

        if os.path.exists(s_file_path) is False:
            s_msg = 'Path given does not exists "{0}"'.format(s_file_path)
            cls.log.error(s_msg)
            raise RuntimeError(s_msg)

        with open(s_file_path, "r") as py_file_data:
            data = json.load(py_file_data)

        if isinstance(data, (dict, list, tuple)) is False:
            s_msg = 'Data read is not a valid BlendShape data "{0}"'.format(s_file_path)
            cls.log.error(s_msg)
            raise RuntimeError(s_msg)

        return data

    def save(self, s_output_path):

        """
        !@Brief Save all SkinCluster found under given root node.

        @type s_output_path: str / unicode
        @param s_output_path: File path.
        """

        self._dump(self.to_dict(), s_output_path)

        return self

    @classmethod
    def save_all(cls, a_nodes, s_output_path):

        """
        !@Brief Save all SkinCluster found under given root node.

        @type a_nodes: Oplist / tuple
        @param a_nodes: Root node name or Root node object.
        @type s_output_path: str / unicode
        @param s_output_path: File path.
        """

        a_data = list()

        if isinstance(s_output_path, str) is False:
            s_msg = "Output path must be a string not {0}".format(type(s_output_path))
            cls.log.error(s_msg)
            raise TypeError(s_msg)

        #   Get all Blendshape
        for n in a_nodes:
            mo_deformer = cls.find(n)
            if mo_deformer is None:
                continue
            a_data.append(BlendShape(mo_deformer).to_dict())

        #   Dump
        cls._dump(a_data, s_output_path)
