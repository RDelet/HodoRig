import os
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
kMessage = "message"
kResetGroup = "resetGroup"


# Maya Colors
class __Color(object):
        
    def __init__(self, name, rgb, maya_index):
        self.name = name
        self.rgb = rgb
        self.maya_index = maya_index
    
    def __str__(self) -> str:
        return self.__repr__()
    
    def __repr__(self) -> str:
        return f"Color(name: {self.name}, rgb: {self.rgb}, MayaIndex: {self.maya_index})"


kColors = [
    __Color("Black", (0, 0, 0), 1),
    __Color("LightBlue", (0, 229, 255), 18),
    __Color("Blue", (0, 0, 153), 6),
    __Color("DarkBlue", (0, 0, 51), 5),
    __Color("LightBrown", (178, 102, 0), 24),
    __Color("Brown", (71, 30, 18), 10),
    __Color("MidBrown", (114, 0, 0), 12),
    __Color("DarkBrown", (41, 15, 10), 11),
    __Color("Green", (0, 255, 0), 14),
    __Color("DarkGreen", (0, 38, 0), 7),
    __Color("LightPink", (0, 0, 255), 20),
    __Color("Purple", (178, 0, 178), 9),
    __Color("DarkPurple", (33, 0, 51), 8),
    __Color("Red", (255, 0, 0), 13),
    __Color("DarkRed", (140, 0, 20), 4),
    __Color("White", (255, 255, 255), 16),
    __Color("LightYellow", (255, 255, 76), 22),
    __Color("Yellow", (255, 255, 0), 17),
    __Color("Black", (0, 0, 0), 1),
    __Color("Black", (0, 0, 0), 1)
]

# Icons
kIconsDir = kModuleDir.parent / "Icons"
kCloseIcon = QtGui.QIcon(str(kIconsDir / "close.svg"))
kPythonIcon = QtGui.QIcon(str(kIconsDir / "python.svg"))
kTrashIcon = QtGui.QIcon(str(kIconsDir / "trash.svg"))
kLockCloseIcon = QtGui.QIcon(str(kIconsDir / "lockClose.svg"))
klockOpenIcon = QtGui.QIcon(str(kIconsDir / "lockOpen.svg"))
kSelectionOnIcon = QtGui.QIcon(str(kIconsDir / "cbSelectionOn.svg"))
kSelectionOffIcon = QtGui.QIcon(str(kIconsDir / "cbSelectionOff.svg"))
