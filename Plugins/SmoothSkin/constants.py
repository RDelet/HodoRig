from enum import Enum
import logging

kToolNameCtx = "SmoothWeightsContext"

log = logging.getLogger(kToolNameCtx)
log.setLevel(logging.INFO)


class SmoothMethod(Enum):
    RELAX = 0
    DISTANCE_WEIGHTED = 1
    HEAT_DIFFUSION = 2
    BARYCENTRIC = 3
    COTANGENT = 4  # ???