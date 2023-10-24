import os

kModuleDir, _ = os.path.split(__file__)

kTemplateDir = os.path.normpath(os.path.join(kModuleDir, "../Templates"))
kTemplateExtension = "hrt"

kShapeDir = os.path.normpath(os.path.join(kModuleDir, "../Shapes"))
kShapeExtension = "json"

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