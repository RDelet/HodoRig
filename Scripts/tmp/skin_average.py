from __future__ import annotations

import numpy as np
from typing import List, Dict

from PySide2 import QtWidgets
from shiboken2 import wrapInstance

from maya import OpenMayaUI as omui
from maya.api import OpenMaya as om, OpenMayaAnim as oma


# ==========================================================
#   Utils
# ==========================================================

_msl = om.MSelectionList()


def _get_maya_window():
    ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(ptr), QtWidgets.QWidget)


def name(obj: str | om.MObject | om.MPlug,
         full: bool = True, namespace: bool = True) -> str:
    if isinstance(obj, om.MDagPath):
        name = obj.fullPathName()
    elif isinstance(obj, om.MPlug):
        node_name = name(obj.node())
        attr_name = om.MFnAttribute(obj.attribute()).name()
        name = f"{node_name}.{attr_name}"
    if isinstance(obj, om.MObject):
        if not obj.hasFn(om.MFn.kDagNode):
            name = om.MFnDependencyNode(obj).name()
        else:
            name = om.MFnDagNode(obj).fullPathName()
    else:
        raise TypeError(f"Argument must be a MObject not {type(obj)}")
    
    if not full:
        name = name.split('|')[-1]
    if not namespace:
        name = name.split(':')[-1]
    
    return name


def get_path(node: str | om.MObject) -> om.MDagPath:
    if isinstance(node, om.MObject):
        if not node.hasFn(om.MFn.kDagNode):
            raise RuntimeError(f"Node {name(node)} is not a dagNode !")
        return om.MDagPath.getAPathTo(node)
    
    try:
        _msl.clear()
        _msl.add(node)
        return _msl.getDagPath(0)
    except RuntimeError:
        raise RuntimeError(f"Node {node} does not exist !")


def harvest(path: om.MDagPath, mfn_type: int) -> om.MObjectArray:
    mit_dg = om.MItDependencyGraph(path.node(), mfn_type,
                                         om.MItDependencyGraph.kUpstream,
                                         om.MItDependencyGraph.kDepthFirst,
                                         om.MItDependencyGraph.kNodeLevel)

    output = om.MObjectArray()
    while mit_dg.isDone() is False:
        output.append(mit_dg.currentNode())
        mit_dg.next()

    return output


# ==========================================================
#   Core
# ==========================================================

class Skin:

    FN_TYPE = om.MFn.kSkinClusterFilter

    def __init__(self, skin_obj: om.MObject):

        self._handle = om.MObjectHandle(skin_obj)
        self._mfn = oma.MFnSkinCluster(skin_obj)
        self._filter = oma.MFnGeometryFilter(skin_obj)
        self._shape = get_path(self.outputs_geometry()[0])
        self._orig_shape = get_path(self.outputs_geometry()[0])
    
    @property
    def obj(self) -> om.MObject:
        return self._handle.object()

    def outputs_geometry(self) -> om.MObjectArray:
        output_geom = om.MObjectArray()
        if self.obj:
            output_geom = self._filter.getOutputGeometry()

        return output_geom

    def inputs_geometry(self) -> om.MObjectArray:
        input_geom = om.MObjectArray()
        if self.skin_obj:
            input_geom = self._filter.getInputGeometry()

        return input_geom

    def get_influences(self) -> Dict[str, int]:

        ids = list()
        influences = list()

        influences_paths = self._mfn.influenceObjects()
        for path in influences_paths:
            ids.append(self._mfn.indexForInfluenceObject(path))
            influences.append(path.fullPathName())

        return {name: inf_id for name, inf_id in zip(influences, ids)}

    @classmethod
    def find_from_path(cls, path: om.MDagPath) -> Skin:
        nodes = om.MObjectArray()
        if path.hasFn(om.MFn.kTransform):
            mfn = om.MFnTransform(path)
            for i in range(mfn.childCount()):
                child = mfn.child(i)
                if child.hasFn(om.MFn.kShape):
                    nodes = harvest(child, cls.FN_TYPE)
                    if len(nodes) > 0:
                        break
        else:
            nodes = harvest(path, cls.FN_TYPE)

        count = len(nodes)
        if count == 0:
            return
        elif count == 1:
            return cls(nodes[0])
        else:
            raise Exception("Multiple node found.")

    def get_weights(self, influence_ids: List[int] | None = None,
                    component_ids: List[int] | None = None) -> np.ndarray:

        single_component = om.MFnSingleIndexedComponent()
        component = single_component.create(om.MFn.kMeshVertComponent)
        mit_vtx = om.MItMeshVertex(self._shape)

        if component_ids:
            for comp_id in component_ids:
                single_component.addElement(comp_id)
        else:
            mit_vtx.reset()
            while not mit_vtx.isDone():
                single_component.addElement(mit_vtx.index())
                mit_vtx.next()

        if influence_ids:
            influence_ids = om.MIntArray(influence_ids)
        else:
            influence_ids = om.MIntArray([x for x in self.get_influences().values()])

        weights = self._mfn.getWeights(self._shape, component, influence_ids)

        return np.array(weights).reshape(single_component.elementCount, len(influence_ids))
    
    def set_weights(self, weights: om.MDoubleArray, influence_ids: List[int] | None = None,
                     component_ids: List[int] | None = None,
                     normalize: bool = False) -> om.MDoubleArray:

        single_component = om.MFnSingleIndexedComponent()
        component = single_component.create(om.MFn.kMeshVertComponent)
        mit_vtx = om.MItMeshVertex(self._shape)

        if component_ids:
            for comp_id in component_ids:
                single_component.addElement(comp_id)
        else:
            mit_vtx.reset()
            while not mit_vtx.isDone():
                single_component.addElement(mit_vtx.index())
                mit_vtx.next()
        
        if influence_ids:
            influence_ids = om.MIntArray(influence_ids)
        else:
            influence_ids = om.MIntArray([x for x in self.get_influences().values()])

        return self._mfn.setWeights(self._shape,
                                    component,
                                    influence_ids,
                                    weights,
                                    normalize, returnOldWeights=True)


# ==========================================================
#   UI
# ==========================================================

class SkinAverage(QtWidgets.QDialog):
    
    def __init__(self):
        super().__init__(_get_maya_window())
        self.setWindowTitle("Skin Average")
        self._build_ui()

        self._skin = None
        self._weights = None
    
    def _build_ui(self):

        self._layout = QtWidgets.QVBoxLayout(self)
        self._layout.setContentsMargins(2, 2, 2, 2)
        self._layout.setSpacing(2)
        
        get_button = QtWidgets.QPushButton("Get")
        get_button.clicked.connect(self._get_weights)
        self._layout.addWidget(get_button)

        set_layout = QtWidgets.QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(2)
        self._layout.addLayout(set_layout)

        set_button = QtWidgets.QPushButton("Set Average")
        set_button.clicked.connect(self._set_weights_average)
        set_layout.addWidget(set_button)

        set_button = QtWidgets.QPushButton("Set Distance")
        set_button.clicked.connect(self._set_weights_distance)
        set_layout.addWidget(set_button)
    
    def _get_weights(self):
        path, components = self._get_selected_components()

        self._skin = Skin.find_from_path(path)
        if not self._skin:
            raise RuntimeError(f"Node {path.fullPathName()} does not have skinCluster !")
        
        self._weights = self._skin.get_weights(component_ids=components)
    
    def _set_weights_average(self):
        path, components = self._get_selected_components()

        skin = Skin.find_from_path(path)
        if not skin:
            raise RuntimeError(f"Node {path.fullPathName()} does not have skinCluster !")
        
        avg_weights = self._weights.mean(axis=0)
        weights = avg_weights / avg_weights.sum()
        skin.set_weights(om.MDoubleArray(weights.flatten().tolist()), component_ids=components)
    
    def _set_weights_distance(self):
        raise NotImplementedError("_set_weights_distance not implemented yet !")

    def _get_selected_components(self):

        msl = om.MGlobal.getActiveSelectionList()

        node_path = None
        components = []
        for i in range(msl.length()):
            current_path, current_components = msl.getComponent(0)
            if not node_path:
                node_path = current_path
            elif node_path.fullPathName() != current_path.fullPathName():
                raise RuntimeError("Select vertices on same mesh !")
                
            if current_components.hasFn(om.MFn.kMeshVertComponent):
                mfn_component = om.MFnSingleIndexedComponent(current_components)
                for j in range(mfn_component.elementCount):
                    components.append(mfn_component.element(j))
            # ToDo: Add case to get vertex from edge and polygon

        return node_path, components


widget = SkinAverage()
widget.show()