from pathlib import Path

try:
    from PySide2 import QtGui
except:
    from PySide6 import QtGui

from maya.api import OpenMaya


kModuleDir = Path(__file__).parent

kSkinExtension = "skin"

kTemplateDir = kModuleDir.parent / "Templates"
kTemplateExtension = "hrt"

kShapeDir = kModuleDir.parent / "Shapes"
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

# Attributes
kClassName = "className"
kManipulators = "manipulators"
kManipulatorType = "manipulatorType"
kMessage = "message"
kResetGroup = "resetGroup"
kString = "string"

# Icons
kIconsDir = kModuleDir.parent / "Icons"
kCloseIcon = QtGui.QIcon(str(kIconsDir / "close.svg"))
kPythonIcon = QtGui.QIcon(str(kIconsDir / "python.svg"))
kTrashIcon = QtGui.QIcon(str(kIconsDir / "trash.svg"))
kLockCloseIcon = QtGui.QIcon(str(kIconsDir / "lockClose.svg"))
klockOpenIcon = QtGui.QIcon(str(kIconsDir / "lockOpen.svg"))
kSelectionOnIcon = QtGui.QIcon(str(kIconsDir / "cbSelectionOn.svg"))
kSelectionOffIcon = QtGui.QIcon(str(kIconsDir / "cbSelectionOff.svg"))
