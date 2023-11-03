import os

kModuleDir, _ = os.path.split(__file__)

kTemplateDir = os.path.normpath(os.path.join(kModuleDir, "../Templates"))
kTemplateExtension = "hrt"

kShapeDir = os.path.normpath(os.path.join(kModuleDir, "../Shapes"))
kShapeExtension = "json"
kIconExtension = "png"

# Generic
kMesh = "mesh"
kCurve = "nurbsCurve"
kSurface = "nurbsSurface"
kType = "type"
kPoints = "points"
kRational = "rational"

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