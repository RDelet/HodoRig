"""
from maya import cmds

plugin_path = r"D:\Work\GitHub\HodoRig\Plugins\cone_reader.py"
if not cmds.pluginInfo(plugin_path, query=True, loaded=True):
    cmds.loadPlugin(plugin_path)
"""

from __future__ import annotations

import numpy as np
import math

from maya.api import OpenMaya as om, OpenMayaRender as omr, OpenMayaUI as omui


PLUGIN_VERSION = "1.0.0"
PLUGIN_VENDOR = "Custom"
NODE_NAME = "coneReader"
NODE_ID = om.MTypeId(0x00080101)
LOCATOR_NAME = "coneReaderViz"
LOCATOR_ID = om.MTypeId(0x00080102)
FLOATS_TO_ARRAY_NAME = "floatsToArray"
FLOATS_TO_ARRAY_ID = om.MTypeId(0x00080103)

DRAW_CLASSIFICATION = "drawdb/geometry/coneReaderViz"
DRAW_REGISTRANT_ID = "coneReaderVizPlugin"

CONE_SEGMENTS = 32
LINE_LEN_LABEL = 1.15

_AXIS_NAMES = ["x", "y", "z"]
_AXIS_VECTORS = {"x": np.array([1.0, 0.0, 0.0]),
                 "y": np.array([0.0, 1.0, 0.0]),
                 "z": np.array([0.0, 0.0, 1.0])}
_MATRIX_ROW = {"x": 0, "y": 1, "z": 2}
_IDW_EPS = 1e-9


def maya_useNewAPI():
    pass


def axis_from_matrix(mmatrix: om.MMatrix, axis: str = "x") -> np.ndarray:
    axis_lower = axis.lower()
    row = np.array(mmatrix, dtype=np.float64).reshape(4, 4)[_MATRIX_ROW[axis_lower], :3]
    norm = np.linalg.norm(row)
    return row / norm if norm > 1e-9 else _AXIS_VECTORS[axis_lower]


class ConeReaderVizData(om.MUserData):

    def __init__(self):
        super().__init__(False)

        self.half_angle = 45.0
        self.radius = 1.0
        self.input_dir = np.array([0.0, 0.0, 1.0])
        self.pose_dirs = np.zeros((0, 3))
        self.pose_colors = []
        self.weights = np.array([])
        self.pose_labels = []


class FloatsToArrayNode(om.MPxNode):

    kNodeName = FLOATS_TO_ARRAY_NAME
    kNodeId = FLOATS_TO_ARRAY_ID

    aInput = om.MObject()
    aOutput = om.MObject()

    @classmethod
    def creator(cls):
        return cls()

    @staticmethod
    def initialize():
        nAttr = om.MFnNumericAttribute()
        FloatsToArrayNode.aInput = nAttr.create("input", "i", om.MFnNumericData.kFloat, 0.0)
        nAttr.storable = True
        nAttr.keyable = True
        nAttr.array = True
        nAttr.usesArrayDataBuilder = True
        om.MPxNode.addAttribute(FloatsToArrayNode.aInput)

        tAttr = om.MFnTypedAttribute()
        default_obj = om.MFnDoubleArrayData().create(om.MDoubleArray())
        FloatsToArrayNode.aOutput = tAttr.create("output", "out", om.MFnData.kDoubleArray, default_obj)
        tAttr.storable = False
        tAttr.writable = False
        tAttr.readable = True
        om.MPxNode.addAttribute(FloatsToArrayNode.aOutput)
        om.MPxNode.attributeAffects(FloatsToArrayNode.aInput, FloatsToArrayNode.aOutput)

    def compute(self, plug, data_block):
        # plug.attribute() matches regardless of whether plug is an element or the array itself.
        if plug.attribute() != FloatsToArrayNode.aOutput:
            return

        in_handle = data_block.inputArrayValue(FloatsToArrayNode.aInput)
        n = len(in_handle)
        result = om.MDoubleArray(n, 0.0)

        for i in range(n):
            in_handle.jumpToPhysicalElement(i)
            result[i] = in_handle.inputValue().asFloat()

        out_data = om.MFnDoubleArrayData()
        out_obj = out_data.create(result)
        out_hdl = data_block.outputValue(FloatsToArrayNode.aOutput)
        out_hdl.setMObject(out_obj)
        out_hdl.setClean()


class ConeReaderNode(om.MPxNode):

    kNodeName = NODE_NAME
    kNodeId = NODE_ID

    aInputMatrix = om.MObject()
    aInputAxis = om.MObject()
    aHalfAngle = om.MObject()
    aSample = om.MObject()
    aSampleInput = om.MObject()
    aSamplePose = om.MObject()
    aOutput = om.MObject()
    aWeight = om.MObject()

    def __init__(self):
        super().__init__()
        self._pose_dirs = np.zeros((0, 3), dtype=np.float64)
        self._pose_matrix = np.zeros((0, 0), dtype=np.float64)
        self._boundary_d = 1.0 - math.cos(math.radians(45.0))
        self._pose_dirty = True

    @classmethod
    def creator(cls):
        return cls()

    @staticmethod
    def initialize():

        mAttr = om.MFnMatrixAttribute()
        ConeReaderNode.aInputMatrix = mAttr.create("inputMatrix", "im")
        mAttr.storable = True
        mAttr.keyable = True
        om.MPxNode.addAttribute(ConeReaderNode.aInputMatrix)

        eAttr = om.MFnEnumAttribute()
        ConeReaderNode.aInputAxis = eAttr.create("inputAxis", "ia", 2)
        for i, axis in enumerate(_AXIS_NAMES):
            eAttr.addField(axis.upper(), i)
        eAttr.storable = True
        eAttr.keyable = True
        om.MPxNode.addAttribute(ConeReaderNode.aInputAxis)

        nAttr = om.MFnNumericAttribute()
        ConeReaderNode.aHalfAngle = nAttr.create("halfAngle", "ha", om.MFnNumericData.kFloat, 45.0)
        nAttr.storable = True
        nAttr.keyable = True
        nAttr.setMin(0.1)
        nAttr.setMax(90.0)
        om.MPxNode.addAttribute(ConeReaderNode.aHalfAngle)

        nAttr = om.MFnNumericAttribute()
        ConeReaderNode.aSampleInput = nAttr.createPoint("sampleInput", "si")
        nAttr.storable = True
        nAttr.keyable = False

        tAttr = om.MFnTypedAttribute()
        ConeReaderNode.aSamplePose = tAttr.create("samplePose", "sp", om.MFnData.kDoubleArray)
        tAttr.storable = True
        tAttr.keyable = False

        cAttr = om.MFnCompoundAttribute()
        ConeReaderNode.aSample = cAttr.create("sample", "s")
        cAttr.addChild(ConeReaderNode.aSampleInput)
        cAttr.addChild(ConeReaderNode.aSamplePose)
        cAttr.array = True
        cAttr.usesArrayDataBuilder = True
        om.MPxNode.addAttribute(ConeReaderNode.aSample)

        nAttr = om.MFnNumericAttribute()
        ConeReaderNode.aWeight = nAttr.create("weight", "wt", om.MFnNumericData.kFloat, 0.0)
        nAttr.storable = False
        nAttr.writable = False
        nAttr.readable = True
        nAttr.array = True
        nAttr.usesArrayDataBuilder = True
        om.MPxNode.addAttribute(ConeReaderNode.aWeight)

        nAttr = om.MFnNumericAttribute()
        ConeReaderNode.aOutput = nAttr.create("output", "out", om.MFnNumericData.kFloat, 0.0)
        nAttr.storable = False
        nAttr.writable = False
        nAttr.readable = True
        nAttr.array = True
        nAttr.usesArrayDataBuilder = True
        om.MPxNode.addAttribute(ConeReaderNode.aOutput)

        for src in (ConeReaderNode.aInputMatrix,
                    ConeReaderNode.aInputAxis,
                    ConeReaderNode.aHalfAngle,
                    ConeReaderNode.aSample):
            om.MPxNode.attributeAffects(src, ConeReaderNode.aOutput)
            om.MPxNode.attributeAffects(src, ConeReaderNode.aWeight)

    def setDependentsDirty(self, plug, plug_array):
        attr = plug.attribute()
        if attr in (ConeReaderNode.aSample, ConeReaderNode.aHalfAngle,
                    ConeReaderNode.aInputAxis):
            self._pose_dirty = True
        return super().setDependentsDirty(plug, plug_array)

    def compute(self, plug, data_block):
        attr = plug.attribute()
        if attr not in (ConeReaderNode.aOutput, ConeReaderNode.aWeight):
            return

        mmatrix = data_block.inputValue(ConeReaderNode.aInputMatrix).asMatrix()
        axis_index = data_block.inputValue(ConeReaderNode.aInputAxis).asShort()
        input_dir = axis_from_matrix(mmatrix, _AXIS_NAMES[axis_index])

        if self._pose_dirty:
            half_angle = np.radians(data_block.inputValue(ConeReaderNode.aHalfAngle).asFloat())
            self._boundary_d = 1.0 - math.cos(half_angle)

            sample_handle = data_block.inputArrayValue(ConeReaderNode.aSample)
            dirs_list, payloads = [], []

            while not sample_handle.isDone():
                compound = sample_handle.inputValue()

                si = np.array(compound.child(ConeReaderNode.aSampleInput).asFloat3(), dtype=np.float64)
                dirs_list.append(si / np.linalg.norm(si))

                sp_obj = compound.child(ConeReaderNode.aSamplePose).data()
                if sp_obj.isNull():
                    payloads.append(np.array([], dtype=np.float64))
                else:
                    payloads.append(np.array(om.MFnDoubleArrayData(sp_obj).array(), dtype=np.float64))

                sample_handle.next()

            n = len(dirs_list)
            dirs_arr = np.array(dirs_list) if n else np.zeros((0, 3), dtype=np.float64)
            if n:
                dirs_arr /= np.linalg.norm(dirs_arr, axis=1, keepdims=True)

            n_vals = max((len(v) for v in payloads), default=0)
            pose_matrix = np.zeros((n, n_vals), dtype=np.float64)
            for i, sp in enumerate(payloads):
                pose_matrix[i, :len(sp)] = sp

            self._pose_dirs = dirs_arr
            self._pose_matrix = pose_matrix
            self._pose_dirty = False

        weights = self._compute_weights(input_dir, self._pose_dirs, self._boundary_d)
        result = weights @ self._pose_matrix

        w_handle = data_block.outputArrayValue(ConeReaderNode.aWeight)
        w_builder = w_handle.builder()
        for i, w in enumerate(weights.tolist()):
            w_builder.addElement(i).setFloat(w)
        w_handle.set(w_builder)
        w_handle.setAllClean()

        out_handle = data_block.outputArrayValue(ConeReaderNode.aOutput)
        builder = out_handle.builder()
        for i, v in enumerate(result.tolist()):
            builder.addElement(i).setFloat(v)
        out_handle.set(builder)
        out_handle.setAllClean()

    @staticmethod
    def _compute_weights(input_dir: np.ndarray, pose_dirs: np.ndarray, boundary_d: float) -> np.ndarray:
        dots = np.dot(pose_dirs, input_dir)
        np.clip(dots, -1.0, 1.0, out=dots)
        d = 1.0 - dots
        
        mask = d < boundary_d
        raw = np.zeros(len(pose_dirs), dtype=np.float64)
        d_m = d[mask]
        raw[mask] = (boundary_d - d_m) / (d_m * d_m + _IDW_EPS)

        total = raw.sum()
        if total > 1e-12:
            raw /= total

        return raw


class ConeReaderVisualizerNode(omui.MPxLocatorNode):

    kNodeName = LOCATOR_NAME
    kNodeId = LOCATOR_ID

    aInputMatrix = om.MObject()
    aInputAxis = om.MObject()
    aHalfAngle = om.MObject()
    aInput = om.MObject()
    aWeight = om.MObject()
    aRadius = om.MObject()

    @classmethod
    def creator(cls):
        return cls()

    @staticmethod
    def initialize():

        mAttr = om.MFnMatrixAttribute()
        ConeReaderVisualizerNode.aInputMatrix = mAttr.create("inputMatrix", "inputMatrix")
        mAttr.storable = True
        mAttr.keyable = True
        om.MPxNode.addAttribute(ConeReaderVisualizerNode.aInputMatrix)

        eAttr = om.MFnEnumAttribute()
        ConeReaderVisualizerNode.aInputAxis = eAttr.create("inputAxis", "inputAxis", 2)
        for i, axis in enumerate(_AXIS_NAMES):
            eAttr.addField(axis.upper(), i)
        eAttr.storable = True
        eAttr.keyable = True
        om.MPxNode.addAttribute(ConeReaderVisualizerNode.aInputAxis)

        nAttr = om.MFnNumericAttribute()
        ConeReaderVisualizerNode.aHalfAngle = nAttr.create("halfAngle", "halfAngle", om.MFnNumericData.kFloat, 45.0)
        nAttr.storable = True
        nAttr.keyable = True
        nAttr.setMin(0.1)
        nAttr.setMax(180.0)
        om.MPxNode.addAttribute(ConeReaderVisualizerNode.aHalfAngle)

        nAttr = om.MFnNumericAttribute()
        ConeReaderVisualizerNode.aRadius = nAttr.create("radius", "radius", om.MFnNumericData.kFloat, 1.0)
        nAttr.storable = True
        nAttr.keyable = True
        nAttr.setMin(0.01)
        om.MPxNode.addAttribute(ConeReaderVisualizerNode.aRadius)

        nAttr = om.MFnNumericAttribute()
        ConeReaderVisualizerNode.aInput = nAttr.createPoint("input", "input")
        nAttr.storable = True
        nAttr.keyable = False
        nAttr.array = True
        nAttr.usesArrayDataBuilder = True
        om.MPxNode.addAttribute(ConeReaderVisualizerNode.aInput)

        nAttr = om.MFnNumericAttribute()
        ConeReaderVisualizerNode.aWeight = nAttr.create("weight", "weight", om.MFnNumericData.kFloat, 0.0)
        nAttr.storable = True
        nAttr.keyable = True
        nAttr.array = True
        nAttr.usesArrayDataBuilder = True
        om.MPxNode.addAttribute(ConeReaderVisualizerNode.aWeight)

    def compute(self, plug, data_block):
        return

    def isBounded(self):
        return True

    def boundingBox(self):
        r = 2.0
        return om.MBoundingBox(om.MPoint(-r, -r, -r), om.MPoint(r, r, r))


class ConeReaderVizDrawOverride(omr.MPxDrawOverride):

    @staticmethod
    def creator(obj):
        return ConeReaderVizDrawOverride(obj)

    def __init__(self, obj):
        super().__init__(obj, None, False)

    def supportedDrawAPIs(self):
        return omr.MRenderer.kOpenGL | omr.MRenderer.kDirectX11 | omr.MRenderer.kOpenGLCoreProfile

    def hasUIDrawables(self):
        return True

    def isBounded(self, obj_path, camera_path):
        return True

    def boundingBox(self, obj_path, camera_path):
        return om.MBoundingBox(om.MPoint(-2, -2, -2), om.MPoint(2, 2, 2))

    def prepareForDraw(self, obj_path, camera_path, frame_context, old_data):
        data = old_data if isinstance(old_data, ConeReaderVizData) else ConeReaderVizData()

        node = obj_path.node()
        fn = om.MFnDependencyNode(node)
        data.half_angle = fn.findPlug("halfAngle", False).asFloat()
        data.radius = fn.findPlug("radius", False).asFloat()

        try:
            axis_idx = fn.findPlug("inputAxis", False).asShort()
            mat_obj = fn.findPlug("inputMatrix", False).asMObject()
            mmatrix = om.MFnMatrixData(mat_obj).matrix()
            data.input_dir = axis_from_matrix(mmatrix, _AXIS_NAMES[axis_idx])
        except Exception:
            data.input_dir = np.array([0.0, 0.0, 1.0])

        input_plug = fn.findPlug("input", False)
        n_poses = input_plug.evaluateNumElements()

        pose_dirs_list = []
        data.pose_colors = []
        data.pose_labels = []

        for i in range(n_poses):
            elem = input_plug.elementByPhysicalIndex(i)
            px = elem.child(0).asFloat()
            py = elem.child(1).asFloat()
            pz = elem.child(2).asFloat()
            v = np.array([px, py, pz])
            pose_dirs_list.append(v)
            data.pose_colors.append(v)
            data.pose_labels.append(f"P{i}")

        data.pose_dirs = np.array(pose_dirs_list) if pose_dirs_list else np.zeros((0, 3))

        w_plug = fn.findPlug("weight", False)
        n_w = w_plug.evaluateNumElements()
        data.weights = np.array([w_plug.elementByPhysicalIndex(i).asFloat() for i in range(n_w)])
        if len(data.weights) < n_poses:
            data.weights = np.pad(data.weights, (0, n_poses - len(data.weights)))

        return data

    def addUIDrawables(self, obj_path, draw_mgr, frame_context, data):
        if not isinstance(data, ConeReaderVizData):
            return

        draw_mgr.beginDrawable()

        r = data.radius
        half_rad = math.radians(data.half_angle)
        origin = om.MPoint(0, 0, 0)

        ring_pts = self._cone_ring_points(data.input_dir, half_rad, r, CONE_SEGMENTS)

        # Cone generator lines
        draw_mgr.setColor(om.MColor([0.6, 0.6, 0.6, 0.45]))
        draw_mgr.setLineWidth(1.0)
        gen_step = max(1, CONE_SEGMENTS // 8)
        for i in range(0, CONE_SEGMENTS, gen_step):
            draw_mgr.line(origin, om.MPoint(ring_pts[i]))

        # Cone rim
        draw_mgr.setColor(om.MColor([0.5, 0.5, 0.5, 0.35]))
        for i in range(CONE_SEGMENTS):
            draw_mgr.line(om.MPoint(ring_pts[i]), om.MPoint(ring_pts[(i + 1) % CONE_SEGMENTS]))

        # Pose directions
        for i in range(len(data.pose_dirs)):
            d = data.pose_dirs[i]
            w = float(data.weights[i]) if i < len(data.weights) else 0.0
            col_np = data.pose_colors[i]

            draw_mgr.setLineWidth(1.0 + w * 5.0)
            draw_mgr.setColor(om.MColor([float(col_np[0]), float(col_np[1]), float(col_np[2]), 0.3 + w * 0.7]))
            tip = om.MPoint(d * r)
            draw_mgr.line(origin, tip)

            normal = om.MVector(float(d[0]), float(d[1]), float(d[2]))
            disc_r = (0.03 + w * 0.06) * r
            draw_mgr.setColor(om.MColor([float(col_np[0]), float(col_np[1]), float(col_np[2]), 0.6 + w * 0.4]))
            draw_mgr.circle(tip, normal, disc_r, True)

            label = data.pose_labels[i] if i < len(data.pose_labels) else f"P{i}"
            draw_mgr.setColor(om.MColor([float(col_np[0]), float(col_np[1]), float(col_np[2]), 1.0]))
            draw_mgr.setFontSize(11)
            draw_mgr.text(om.MPoint(d * r * LINE_LEN_LABEL), f"{label}  {w:.2f}", omr.MUIDrawManager.kCenter)

        # Input direction
        id_ = data.input_dir
        draw_mgr.setLineWidth(2.5)
        draw_mgr.setColor(om.MColor([1.0, 1.0, 1.0, 1.0]))
        tip_in = om.MPoint(id_ * r)
        draw_mgr.line(origin, tip_in)

        normal_in = om.MVector(float(id_[0]), float(id_[1]), float(id_[2]))
        draw_mgr.setColor(om.MColor([1.0, 1.0, 0.3, 1.0]))
        draw_mgr.circle(tip_in, normal_in, 0.04 * r, True)

        draw_mgr.setFontSize(10)
        draw_mgr.setColor(om.MColor([1.0, 1.0, 1.0, 1.0]))
        draw_mgr.text(om.MPoint(id_ * r * LINE_LEN_LABEL * 0.9), "IN", omr.MUIDrawManager.kCenter)

        draw_mgr.endDrawable()
    
    @staticmethod
    def _pose_color(direction: np.ndarray) -> np.ndarray:
        v = np.asarray(direction, dtype=np.float64)
        norm = np.linalg.norm(v)
        if norm > 1e-9:
            v = v / norm

        return ((v + 1.0) * 0.5).astype(np.float32)

    @staticmethod
    def _cone_ring_points(axis: np.ndarray, half_angle_rad: float, radius: float, n: int = CONE_SEGMENTS) -> np.ndarray:
        ref = np.array([0.0, 1.0, 0.0])
        if abs(np.dot(axis, ref)) > 0.99:
            ref = np.array([1.0, 0.0, 0.0])

        u = np.cross(axis, ref)
        u /= np.linalg.norm(u)
        v = np.cross(axis, u)

        ring_r = radius * math.tan(half_angle_rad)
        tip = axis * radius

        t = np.linspace(0, 2 * math.pi, n, endpoint=False)
        pts = tip + ring_r * (np.outer(np.cos(t), u) + np.outer(np.sin(t), v))

        return pts.astype(np.float64)


def initializePlugin(plugin):
    fn = om.MFnPlugin(plugin, PLUGIN_VENDOR, PLUGIN_VERSION)

    try:
        fn.registerNode(FloatsToArrayNode.kNodeName,
                        FloatsToArrayNode.kNodeId,
                        FloatsToArrayNode.creator,
                        FloatsToArrayNode.initialize,
                        om.MPxNode.kDependNode)
        om.MGlobal.displayInfo(f"Plugin {FloatsToArrayNode.__name__} registered.")
    except Exception as e:
        om.MGlobal.displayError(f"Plugin {FloatsToArrayNode.__name__} register error: {e}")
        raise

    try:
        fn.registerNode(ConeReaderNode.kNodeName,
                        ConeReaderNode.kNodeId,
                        ConeReaderNode.creator,
                        ConeReaderNode.initialize,
                        om.MPxNode.kDependNode)
        om.MGlobal.displayInfo(f"Plugin {ConeReaderNode.__name__} registered.")
    except Exception as e:
        om.MGlobal.displayError(f"Plugin {ConeReaderNode.__name__} register error: {e}")
        raise

    try:
        fn.registerNode(ConeReaderVisualizerNode.kNodeName,
                        ConeReaderVisualizerNode.kNodeId,
                        ConeReaderVisualizerNode.creator,
                        ConeReaderVisualizerNode.initialize,
                        om.MPxNode.kLocatorNode,
                        DRAW_CLASSIFICATION)
        omr.MDrawRegistry.registerDrawOverrideCreator(DRAW_CLASSIFICATION,
                                                      DRAW_REGISTRANT_ID,
                                                      ConeReaderVizDrawOverride.creator)
        om.MGlobal.displayInfo(f"Plugin {ConeReaderVisualizerNode.__name__} registered.")
    except Exception as e:
        om.MGlobal.displayError(f"Plugin {ConeReaderVisualizerNode.__name__} register error: {e}")
        raise


def uninitializePlugin(plugin):
    fn = om.MFnPlugin(plugin)

    try:
        fn.deregisterNode(FloatsToArrayNode.kNodeId)
        om.MGlobal.displayInfo(f"Plugin {FloatsToArrayNode.__name__} unregistered.")
    except Exception as e:
        om.MGlobal.displayError(f"Plugin {FloatsToArrayNode.__name__} unregister error: {e}")
        raise

    try:
        fn.deregisterNode(ConeReaderNode.kNodeId)
        om.MGlobal.displayInfo(f"Plugin {ConeReaderNode.__name__} unregistered.")
    except Exception as e:
        om.MGlobal.displayError(f"Plugin {ConeReaderNode.__name__} unregister error: {e}")
        raise

    try:
        omr.MDrawRegistry.deregisterDrawOverrideCreator(DRAW_CLASSIFICATION, DRAW_REGISTRANT_ID)
        fn.deregisterNode(ConeReaderVisualizerNode.kNodeId)
        om.MGlobal.displayInfo(f"Plugin {ConeReaderVisualizerNode.__name__} unregistered.")
    except Exception as e:
        om.MGlobal.displayError(f"Plugin {ConeReaderVisualizerNode.__name__} unregister error: {e}")
        raise