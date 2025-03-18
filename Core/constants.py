from pathlib import Path
from typing import TypeVar

try:
    from PySide2 import QtGui
except:
    from PySide6 import QtGui

from maya.api import OpenMaya


T = TypeVar("T")


kModuleDir = Path(__file__).parent.parent
kModuleName = kModuleDir.name

kSkinExtension = "skin"

kTemplateDir = kModuleDir / "Templates"
kTemplateExtension = "hrt"

kShapeDir = kModuleDir / "Shapes"
kShapeExtension = "json"
kIconExtension = "png"


# Generic
kMesh = "mesh"
kMeshApi = OpenMaya.MFn.kMesh
kCurve = "nurbsCurve"
kCurveApi = OpenMaya.MFn.kNurbsCurve
kSurface = "nurbsSurface"
kSurfaceApi = OpenMaya.MFn.kNurbsSurface

kTypeToApi = {kMesh: kMeshApi, kCurve: kCurveApi, kSurface: kSurfaceApi}
kApiToType = {kMeshApi: kMesh, kCurveApi: kCurve, kSurfaceApi: kSurface}

kType = "type"
kPoints = "points"
kRational = "rational"
kWorld = OpenMaya.MSpace.kWorld
kObject = OpenMaya.MSpace.kObject


# Nodes
kTransform = "transform"
kNetwork = "network"


# Mesh
kNumVertices = "numVertices"
kNumPolygons = "numPolygons"
kPolygonCounts = "polygonCounts"
kPolygonConnects = "polygonConnects"
kUv = "uv"


# Curve
kKnots = "knots"
kForm = "form"
kDegrees = "degrees"
k2D = "curve2D"


# Surface
kKnotsU = "knotsU"
kKnotsV = "knotsV"
kFormU = "formU"
kFormV = "formV"
kDegreeU = "degreeU"
kDegreeV = "degreeV"


# Manip types
kFk = "FK"


# Attributes Type
kBool = "bool"
kByte = "byte"
kChar = "char"
kCompound = "compound"
kDouble = "double"
kDoubleAngle = "doubleAngle"
kDoubleLinear = "doubleLinear"
kEnum = "enum"
kFloat = "float"
kFloatAngle = "floatAngle"
kFloatLinear = "floatLinear"
kLong = "long"
kMessage = "message"
kShort = "short"
kTime = "time"
kAttributeTypes = [kBool, kByte, kChar, kCompound, kDouble, kDoubleAngle,
                   kDoubleLinear, kEnum, kFloat, kFloatAngle, kFloatLinear,
                   kLong, kMessage, kShort, kTime]


# Attributes DataType
kString = "string"
kMatrix = "matrix"
kDoubleArray = "doubleArray"
kFloatArray = "floatArray"
kInt32Array = "Int32Array"
kVectorArray = "vectorArray"
kNurbsCurve = "nurbsCurve"
kNurbsSurface = "nurbsSurface"
kMesh = "mesh"
kLattice = "lattice"
kPointArray = "pointArray"
kSpectrumRGB = "spectrumRGB"
kComponentList = "componentList"
kDataTypes = [kString, kMatrix, kDoubleArray, kFloatArray, kInt32Array,
              kVectorArray, kNurbsCurve, kNurbsSurface, kMesh, kLattice,
              kPointArray, kSpectrumRGB, kComponentList]


# Attributes
kClassName = "className"
kManipulators = "manipulators"
kChildren = "children"
kBuilders = "builders"
kParent = "parent"
kManipulatorType = "manipulatorType"
kMessage = "message"
kResetGroup = "resetGroup"
kString = "string"


# Icons
kIconsDir = kModuleDir / "Icons"
kCloseIcon = QtGui.QIcon(str(kIconsDir / "close.svg"))
kPythonIcon = QtGui.QIcon(str(kIconsDir / "python.svg"))
kTrashIcon = QtGui.QIcon(str(kIconsDir / "trash.svg"))
kLockCloseIcon = QtGui.QIcon(str(kIconsDir / "lockClose.svg"))
klockOpenIcon = QtGui.QIcon(str(kIconsDir / "lockOpen.svg"))
kSelectionOnIcon = QtGui.QIcon(str(kIconsDir / "cbSelectionOn.svg"))
kSelectionOffIcon = QtGui.QIcon(str(kIconsDir / "cbSelectionOff.svg"))


# Builders
kShapeScale = "shapeScale"
kShapeDirection = "shapeDir"
## IK
kSolver = "solver"
kSnapRotation = "snapRotation"
kPvDistance = "pvDistance"
## Blend
kBlendName = "blendName"