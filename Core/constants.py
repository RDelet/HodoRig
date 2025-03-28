from pathlib import Path
from typing import TypeVar

try:
    from PySide2 import QtGui
except:
    from PySide6 import QtGui

from maya.api import OpenMaya

from ..Helpers.color import Color


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
kJoint = "joint"
kPointOnCurveInfo = "pointOnCurveInfo"
kNetwork = "network"
kIkRPsolver = "ikRPsolver"
kIkSplineSolver = "ikSplineSolver"
kDistanceBetween = "distanceBetween"
kBlendTwoAttr = "blendTwoAttr"
kMultiplyDivide = "multiplyDivide"


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
kTranslate = "translate"
kTranslateX = "translateX"
kTranslateY = "translateY"
kTranslateZ = "translateZ"
kRotate = "rotate"
kRotateX = "rotateX"
kRotateY = "rotateY"
kRotateZ = "rotateZ"
kScale = "scale"
kScaleX = "scaleX"
kScaleY = "scaleY"
kScaleZ = "scaleZ"
kShear = "shear"
kShearXY = "shearXY"
kShearXZ = "shearXZ"
kShearYZ = "shearYZ"
kVisibility = "visibility"
kClassName = "className"
kManipulators = "manipulators"
kChildren = "children"
kBuilders = "builders"
kParent = "parent"
kManipulatorType = "manipulatorType"
kMessage = "message"
kResetGroup = "resetGroup"
kString = "string"
kInheritsTransform = "inheritsTransform"
kStretch = "stretch"
kParameter = "parameter"
kTurnOnPercentage = "turnOnPercentage"
kLocal = "local"
kInputCurve = "inputCurve"
kWorldMatrix = "worldMatrix"
kDTwistControlEnable = "dTwistControlEnable"
kDWorldUpType = "dWorldUpType"
kDForwardAxis = "dForwardAxis"
kDWorldUpAxis = "dWorldUpAxis"
kDWorldUpVector = "dWorldUpVector"
kDWorldUpVectorEnd = "dWorldUpVectorEnd"
kDWorldUpMatrix = "dWorldUpMatrix"
kDWorldUpMatrixEnd = "dWorldUpMatrixEnd"
kInput = "input"
kInput1 = "input1"
kInput1X = "input1X"
kInput1Y = "input1Y"
kInput1Z = "input1Z"
kInput2 = "input2"
kInput2X = "input2X"
kInput2Y = "input2Y"
kInput2Z = "input2Z"
kOutput = "output"
kOutputX = "outputX"
kOutputY = "outputY"
kOutputZ = "outputZ"
kPoint1 = "point1"
kPoint1X = "point1X"
kPoint1Y = "point1Y"
kPoint1Z = "point1Z"
kPoint2 = "point2"
kPoint2X = "point2X"
kPoint2Y = "point2Y"
kPoint2Z = "point2Z"
kDistance = "distance"
kPosition = "position"
kPositionX = "positionX"
kPositionY = "positionY"
kPositionZ = "positionZ"
kAttributesBlender = "attributesBlender"

# Colors
kBlaack = Color.get("black")
kLightBlue = Color.get("lightBlue")
kBlue = Color.get("blue")
kDarkBlue = Color.get("darkBlue")
kLightBrown = Color.get("lightBrown")
kBrown = Color.get("brown")
kMidBrown = Color.get("midBrown")
kDarkBrown = Color.get("darkBrown")
kGreen = Color.get("green")
kDarkGreen = Color.get("darkGreen")
kLightPink = Color.get("lightPink")
kPurple = Color.get("purple")
kDarkPurple = Color.get("darkPurple")
kRed = Color.get("red")
kDarkRed = Color.get("darkRed")
kWhite = Color.get("white")
kLightYellow = Color.get("lightYellow")
kYellow = Color.get("yellow")


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