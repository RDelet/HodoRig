import logging
import numpy as np
import time

from maya.api import OpenMaya as om


log = logging.getLogger("LinearBlendSkin")
log.setLevel(logging.DEBUG)


def maya_useNewAPI():
    pass


class LinearBlendSkin(om.MPxNode):

    kPluginName = "linearBlendSkin"
    kPluginNodeID = om.MTypeId(0x1851328)

    ENVELOPE = None
    INPUT_GEOM = None
    OUTPUT_GEOM = None
    MATRICES = None
    BIND_MATRICES = None
    WEIGHTS = None

    @classmethod
    def creator(cls):
        return cls()

    def __init__(self):
        super(LinearBlendSkin, self).__init__()

        self._envelope = 1.0
        self._input_geom = None
        self._matrix_count = 0
        self._bind_matrices = None
        self._matrices = None
        self._orig_points = None
        self._weights = None
        self._output_fn = None

    @classmethod
    def initialize(cls):
        
        # Enveloppe
        numeric_attr = om.MFnNumericAttribute()
        cls.ENVELOPE = numeric_attr.create("envelope", "en", om.MFnNumericData.kFloat, 1.0)
        numeric_attr.keyable = True
        numeric_attr.setMin(0.0)
        numeric_attr.setMax(1.0)
        cls.addAttribute(cls.ENVELOPE)
        
        # Input Geometry
        typed_attr = om.MFnTypedAttribute()
        cls.INPUT_GEOM = typed_attr.create("inputGeometry", "ig", om.MFnData.kMesh)
        typed_attr.storable = False
        typed_attr.writable = True
        cls.addAttribute(cls.INPUT_GEOM)
        
        # Matrices
        matrix_attr = om.MFnMatrixAttribute()
        cls.MATRICES = matrix_attr.create("matrix", "m")
        matrix_attr.array = True
        cls.addAttribute(cls.MATRICES)
        
        # Bind Matrices
        matrix_attr = om.MFnMatrixAttribute()
        cls.BIND_MATRICES = matrix_attr.create("bindMatrix", "bm")
        matrix_attr.array = True
        cls.addAttribute(cls.BIND_MATRICES)
        
        # Weights
        numeric_attr = om.MFnNumericAttribute()
        cls.WEIGHTS = numeric_attr.create("weights", "w", om.MFnNumericData.kDouble, 0.0)
        numeric_attr.array = True
        cls.addAttribute(cls.WEIGHTS)

        # Output Geometry
        typed_attr = om.MFnTypedAttribute()
        cls.OUTPUT_GEOM = typed_attr.create("outputGeometry", "og", om.MFnData.kMesh)
        typed_attr.storable = False
        typed_attr.writable = True
        cls.addAttribute(cls.OUTPUT_GEOM)
        
        # Attributs affects
        cls.attributeAffects(cls.ENVELOPE, cls.OUTPUT_GEOM)
        cls.attributeAffects(cls.INPUT_GEOM, cls.OUTPUT_GEOM)
        cls.attributeAffects(cls.MATRICES, cls.OUTPUT_GEOM)
        cls.attributeAffects(cls.BIND_MATRICES, cls.OUTPUT_GEOM)
        cls.attributeAffects(cls.WEIGHTS, cls.OUTPUT_GEOM)
        
        return True

    def compute(self, plug, data):

        if plug != self.OUTPUT_GEOM:
            return

        self._envelope = data.inputValue(self.ENVELOPE).asFloat()

        if not self._get_input_mesh(data):
            log.debug("No input mesh.")
            return

        if not self._get_matrices(data):
            log.debug("No matrices.")
            return

        if not self._get_weights(data):
            log.debug("No weights.")
            return        

        output_handle = data.outputValue(self.OUTPUT_GEOM)
        output_handle.setMObject(self._lbs())
        data.setClean(plug)

        return
    
    def _get_input_mesh(self, data: om.MDataBlock) -> bool:
        self._input_geom = data.inputValue(self.INPUT_GEOM).asMesh()
        if self._input_geom.isNull():
            return False

        mesh_fn = om.MFnMesh(self._input_geom)
        self._orig_points = np.array(mesh_fn.getPoints(om.MSpace.kObject))

        return True

    def _get_matrices(self, data: om.MDataBlock) -> bool:

        matrices = []
        matrix_handle = data.inputArrayValue(self.MATRICES)
        while not matrix_handle.isDone():
            matrix = matrix_handle.inputValue().asMatrix()
            matrices.append(np.array(matrix).reshape(4, 4))
            matrix_handle.next()
        
        # Update on attribute change
        bind_matrices = []  
        bind_matrix_handle = data.inputArrayValue(self.BIND_MATRICES)
        while not bind_matrix_handle.isDone():
            matrix = bind_matrix_handle.inputValue().asMatrix()
            bind_matrices.append(np.array(matrix).reshape(4, 4))
            bind_matrix_handle.next()

        self._matrix_count = len(matrices)
        if self._matrix_count == 0 or self._matrix_count != len(bind_matrices):
            return False

        self._bind_matrices = np.array(bind_matrices)
        self._matrices = np.array(matrices)

        return True
    
    def _get_weights(self, data: om.MDataBlock) -> bool:
        # Update on attr change
        weights = []
        weights_handle = data.inputArrayValue(self.WEIGHTS)
        while not weights_handle.isDone():
            weights.append(weights_handle.inputValue().asDouble())
            weights_handle.next()

        weight_count = len(weights)
        if weight_count != len(self._orig_points) * self._matrix_count:
            return False
        
        self._weights = np.array(weights).reshape(self._matrix_count, len(self._orig_points))
        self._weights *= self._envelope
        
        return True

    def _lbs(self):
        """!@Brief Applies Linear Blend Skinning to deform the mesh vertices.
                   The transformation of a vertex is computed as follows:
                       p' = Σ (w_i * (M_i @ B_i @ p))
                   
                   where:
                   - p' is the transformed vertex position.
                   - w_i is the vertex weight for influence i (weights sum to 1).
                   - M_i is the world transformation matrix of influence i.
                   - B_i is the inverse bind pose matrix of influence i.
                   - p is the original vertex position in homogeneous coordinates (x, y, z, 1).
        """
        transform_matrix = self._bind_matrices @ self._matrices
        transformed_points = np.tensordot(self._orig_points, transform_matrix, axes=([1], [1]))
        weighted_points = np.sum(transformed_points * self._weights.T[..., np.newaxis], axis=1)

        mesh_data = om.MFnMeshData().create()
        om.MFnMesh().copy(self._input_geom, mesh_data)
        output_fn = om.MFnMesh(mesh_data)
        output_fn.setPoints(om.MPointArray(weighted_points), om.MSpace.kObject)

        return mesh_data


def initializePlugin(obj):
    plugin = om.MFnPlugin(obj, "Remi Deletrain -- remi.deletrain@gmail.com", "2.0", "Any")
    try:
        plugin.registerNode(
            LinearBlendSkin.kPluginName,
            LinearBlendSkin.kPluginNodeID,
            LinearBlendSkin.creator,
            LinearBlendSkin.initialize,
            om.MPxNode.kDependNode
        )
    except Exception as e:
        raise RuntimeError(f"Failed to register node: {LinearBlendSkin.kPluginName}, Error: {str(e)}")


def uninitializePlugin(obj):
    plugin = om.MFnPlugin(obj)
    try:
        plugin.deregisterNode(LinearBlendSkin.kPluginNodeID)
    except Exception as e:
        raise RuntimeError(f"Failed to deregister node: {LinearBlendSkin.kPluginName}, Error: {str(e)}")
