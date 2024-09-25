"""
!@Brief

from __future__ import annotations

from maya import cmds
from maya.api import OpenMaya


effectors = ["BB_L_0_Hand", "BB_R_0_Hand", "BB_L_0_Foot", "BB_R_0_Foot", "BB_M_0_Head"]
root = "BB_M_0_Root"
segments = []


def find_fabrik_segments(root: str, parent: Segment = None):
    output = []
    start_pos = OpenMaya.MVector(cmds.xform(root, query=True, translation=True, worldSpace=True))
    children = cmds.listRelatives(root, children=True, fullPath=True, type="joint") or []
    for child in children:
        end_pos = OpenMaya.MVector(cmds.xform(child, query=True, translation=True, worldSpace=True))
        segment = Segment(start_pos, end_pos, parent=parent, is_effector=child.split("|")[-1] in effectors)
        print(f'{root.split("|")[-1]} -> {child.split("|")[-1]}', segment)
        output.append(segment)
        if not segment.is_effector:
            output.extend(find_fabrik_segments(child, parent=segment))
    
    return output

segments = find_fabrik_segments(root)

"""

from __future__ import annotations

import logging
import traceback

from maya import OpenMaya, OpenMayaMPx


log = logging.getLogger("ikNBone")
log.setLevel(logging.DEBUG)


class Segment:

    def __init__(self, start_point: OpenMaya.MVector, end_point: OpenMaya.MVector,
                 parent: Segment, is_effector: bool = False, target: OpenMaya.MVector = None):
        self._is_effector = is_effector
        self._parent = parent
        self.end_point = end_point
        self.start_point = start_point
        self._length = (self.end_point - self.start_point).length()
        self.target = target if target else end_point
    
    def __str__(self):
        return self.__repr__()
    
    def __repr__(self):
        return f"{self.__class__.__name__}(isEffector: {self._is_effector}, length: {self._length})"
        
    @property
    def is_effector(self):
        return self._is_effector

    @property
    def length(self):
        return self._length

    @property
    def parent(self):
        return self._parent


class IKSolver:

    def __init__(self, max_iteration: int = 100, min_distance: float = 1e-2):
        self._max_iteration = max_iteration
        self._min_distance = min_distance
    
    def solve(self, *args, **kwargs):
        raise RuntimeError(f"Function {self.__class__.__name__}.solve need to be reimplemented !")


class FABRIKSimpleChain(IKSolver):
    
    def solve(self, points, target):
        origin = points[0]
        segment_length = [(points[i + 1] - points[i]).length() for i in range(len(points) - 1)]

        for iteration in range(self.max_iteration):
            starting_from_target = iteration % 2 == 0
            # Reverse arrays to alternate between forward and backward passes
            points = [x for x in reversed(points)]
            segment_length = [x for x in reversed(segment_length)]
            points[0] = target if starting_from_target else origin
            # Constrain lengths
            for i in range(1, len(points)):
                norm_dir = (points[i] - points[i - 1]).normal()
                points[i] = points[i - 1] + norm_dir * segment_length[i - 1]
            # Terminate if close enough to target
            if starting_from_target:
                if (points[-1] - target).length() <= self.min_distance:
                    break
        
        return points


class FABRIK(Solver):
    
    def _front_reaching(self, effector: Segment):
        if effector.target is not None:
            effector.end_point = effector.target

        current_segment = effector

        while current_segment.parent is not None:
            parent_segment = current_segment.parent
            direction = (current_segment.start_point - parent_segment.end_point).normal()
            parent_segment.end_point = current_segment.start_point - direction * parent_segment.length
            current_segment = parent_segment

    def _back_reaching(self, root_segment: Segment, segments: list):
        current_segment = root_segment

        while current_segment is not None:
            if current_segment.parent is None:
                current_segment.start_point = root_segment.start_point

            for child_segment in segments:
                if child_segment.parent == current_segment:
                    direction = (child_segment.end_point - current_segment.start_point).normal()
                    child_segment.start_point = current_segment.start_point + direction * current_segment.length

            current_segment = current_segment.parent

    def _effectors_close_enough(self, segments: list) -> bool:
        for segment in segments:
            if segment.is_effector and segment.target is not None:
                if (segment.end_point - segment.target).length() > self.min_distance:
                    return False
        return True

    def solve(self, segments: list) -> list:
        for iteration in range(self.max_iteration):
            starting_from_targets = iteration % 2 == 0

            if starting_from_targets:
                for segment in segments:
                    if segment.is_effector:
                        self._front_reaching(segment)
            else:
                root_segments = {seg.parent for seg in segments if seg.parent is not None}
                for root_segment in root_segments:
                    self._back_reaching(root_segment, segments)

            if starting_from_targets and self._effectors_close_enough(segments):
                break

        return segments


class IkNBone(OpenMayaMPx.MPxNode):

    kPluginNode = 'IkNBone'
    kPluginNodeID = OpenMaya.MTypeId(0x1851368)
    kPluginNodeType = OpenMayaMPx.MPxNode.kDependNode

    MATRIX = OpenMaya.MObject()
    TARGET = OpenMaya.MObject()
    MAX_ITER = OpenMaya.MObject()
    MIN_DIST = OpenMaya.MObject()

    OUT_MATRIX = OpenMaya.MObject()

    @classmethod
    def creator(cls):
        return OpenMayaMPx.asMPxPtr(cls())

    def __init__(self):
        super(IkNBone, self).__init__()

        self._ik_solver = FABRIKSolver()
        self._target_pos = OpenMaya.MVector()
        self._points = list()

    def compute(self, plug, data):
        if plug != self.OUT_MATRIX:
            return

        self._get_data(data)
        self._compute_points(data)
        self._set_output(plug, data)

    def _get_data(self, data):
        self._ik_solver.max_iteration = data.inputValue(self.MAX_ITER).asInt()
        self._ik_solver.min_distance = data.inputValue(self.MIN_DIST).asDouble()
        target_matrix = data.inputValue(self.TARGET).asMatrix()
        self._target_pos = OpenMaya.MVector(target_matrix(3, 0),
                                            target_matrix(3, 1),
                                            target_matrix(3, 2))
    
    def _compute_points(self, data):
        self._update_points(data)
        if not self._points:
            return
        self._points = self._ik_solver.solve(self._points, self._target_pos)

    def _set_output(self, plug, data):
        outputs_handle = data.outputArrayValue(self.OUT_MATRIX)
        for i in range(len(self._points)):
            transformation_matrix = OpenMaya.MTransformationMatrix()
            transformation_matrix.setTranslation(self._points[i], OpenMaya.MSpace.kWorld)
            outputs_handle.jumpToElement(i)
            output_handle = outputs_handle.outputValue()
            output_handle.setMMatrix(transformation_matrix.asMatrix())

        data.setClean(plug)

    def _update_points(self, data):
        matrix_handle = data.inputArrayValue(self.MATRIX)
        count = matrix_handle.elementCount()
        if count != len(self._points):
            self._points = list()
            for i in range(count):
                matrix_handle.jumpToElement(i)
                matrix = matrix_handle.inputValue().asMatrix()
                point = OpenMaya.MVector(matrix(3, 0), matrix(3, 1), matrix(3, 2))
                self._points.append(point)

    @classmethod
    def initializer(cls):

        in_attributes = list()
        out_attributes = list()

        double_attr = OpenMaya.MFnNumericData.kDouble
        int_attr = OpenMaya.MFnNumericData.kInt

        #   ==============================
        #   Input attributes

        matrix_attr = OpenMaya.MFnMatrixAttribute()
        cls.MATRIX = matrix_attr.create('inMatrix', 'inMatrix')
        matrix_attr.setKeyable(False)
        matrix_attr.setStorable(True)
        matrix_attr.setArray(True)
        in_attributes.append(cls.MATRIX)

        target_attr = OpenMaya.MFnMatrixAttribute()
        cls.TARGET = target_attr.create('targetMatrix', 'targetMatrix')
        target_attr.setKeyable(False)
        target_attr.setStorable(True)
        in_attributes.append(cls.TARGET)

        max_iter_attr = OpenMaya.MFnNumericAttribute()
        cls.MAX_ITER = max_iter_attr.create("maxIteration", "maxIteration", int_attr, 100)
        max_iter_attr.setKeyable(True)
        max_iter_attr.setStorable(True)
        in_attributes.append(cls.MAX_ITER)

        min_dist_attr = OpenMaya.MFnNumericAttribute()
        cls.MIN_DIST = min_dist_attr.create("minDistance", "minDistance", double_attr, 1e-2)
        min_dist_attr.setKeyable(True)
        min_dist_attr.setStorable(True)
        in_attributes.append(cls.MIN_DIST)

        #   ==============================
        #   Output attributes

        out_matrix_attr = OpenMaya.MFnMatrixAttribute()
        cls.OUT_MATRIX = out_matrix_attr.create("outMatrix", "outMatrix")
        out_matrix_attr.setKeyable(False)
        out_matrix_attr.setStorable(False)
        out_matrix_attr.setHidden(False)
        out_matrix_attr.setArray(True)
        out_attributes.append(cls.OUT_MATRIX)

        #   Add attributes
        for attribute in in_attributes + out_attributes:
            cls.addAttribute(attribute)

        #   Set the attribute dependencies
        for out_attr in out_attributes:
            for in_attr in in_attributes:
                cls.attributeAffects(in_attr, out_attr)


# noinspection PyPep8Naming
def initializePlugin(obj):
    plugin = OpenMayaMPx.MFnPlugin(obj, "Remi Deletrain -- remi.deletrain@gmail.com", "1.0", "Any")
    try:
        plugin.registerNode(IkNBone.kPluginNode,
                            IkNBone.kPluginNodeID,
                            IkNBone.creator,
                            IkNBone.initializer,
                            IkNBone.kPluginNodeType)
    except Exception:
        log.debug(traceback.format_exc())
        raise RuntimeError(f"Failed to register command: {IkNBone.kPluginNode}")


# noinspection PyPep8Naming
def uninitializePlugin(m_object):
    plugin = OpenMayaMPx.MFnPlugin(m_object)
    try:
        plugin.deregisterNode(IkNBone.kPluginNodeID)
    except Exception:
        log.debug(traceback.format_exc())
        raise RuntimeError(f"Failed to register command: {IkNBone.kPluginNode,}")
