from __future__ import annotations
from typing import Optional
import math
import numpy as np

from maya import cmds
from maya.api import OpenMaya as om, OpenMayaUI as omui, OpenMayaRender as omr

from . import constants
from .smoothSkin import Skin, get_path
from .smoothSkin import SmoothMethod


class SmoothSkinCtx(omui.MPxContext):

    SINGLETON = None

    def __init__(self):
        super().__init__()

        if SmoothSkinCtx.SINGLETON is None:
            SmoothSkinCtx.SINGLETON = self

        self._radius = 0.01
        self._mouse_pos = [0, 0]
        self._relaxx_factor = 0.5
        self._smooth_method = SmoothMethod.RELAX
    
    @property
    def radius(self) -> float:
        return self._radius
    
    @radius.setter
    def radius(self, value: float):
        self._radius = value
        
    def toolOnSetup(self, event):
        self.reset_context()
        try:
            self._dag_path = get_path(cmds.ls(selection=True, long=True)[0])
            self._mesh_fn = om.MFnMesh(self._dag_path)
            self._skin = Skin.find(self._dag_path.node())
        except Exception as e:
            constants.log.error(f"Error: {e}")

    def toolOffCleanup(self):
        self.reset_context()

    def doPress(self, event: om.MEvent, draw_mgt: omr.MUIDrawManager, context: omr.MFrameContext):
        constants.log.debug(f"{self.__class__.__name__}.doPress")
        self._mouse_pos = event.position
        self._draw_circle(draw_mgt)
    
    def doPressLegacy(self, event: om.MEvent):
        constants.log.debug(f"{self.__class__.__name__}.doPressLegacy")
    
    def doEnterRegion(self, event: om.MEvent):
        constants.log.debug(f"{self.__class__.__name__}.doEnterRegion")
    
    def doHold(self, event: om.MEvent, draw_mgt: omr.MUIDrawManager, context: omr.MFrameContext):
        constants.log.debug(f"{self.__class__.__name__}.doHold")
    
    def doHoldLegacy(self, event: om.MEvent):
        constants.log.debug(f"{self.__class__.__name__}.doHoldLegacy")

    def doDrag(self, event: om.MEvent, draw_mgt: omr.MUIDrawManager, context: omr.MFrameContext):
        constants.log.debug(f"{self.__class__.__name__}.doDrag")
        self._mouse_pos = event.position
        self._draw_circle(draw_mgt)

        if not self._skin:
            return

        hit_point = self._get_hit_point()
        if not hit_point:
            return

        vertex_ids = self._getVerticesWithinRadius(hit_point)
        if len(vertex_ids) == 0:
            return

        self._skin.smooth(self._smooth_method, relax_factor=self._relaxx_factor, vertex_ids=vertex_ids)
        cmds.refresh(force=True)
    
    def _getVerticesWithinRadius(self, hitPoint):
        view = omui.M3dView.active3dView()
        verticesInRadius = []
        points = self._mesh_fn.getPoints(om.MSpace.kWorld)
        hitScreen = view.worldToView(om.MPoint(hitPoint))
        for i, pt in enumerate(points):
            screenPt = view.worldToView(pt)
            dist = math.hypot(screenPt[0] - hitScreen[0], screenPt[1] - hitScreen[1])
            if dist <= self._radius:
                verticesInRadius.append(i)

        return np.array(verticesInRadius)
    
    def doDragLegacy(self, event: om.MEvent):
        constants.log.debug(f"{self.__class__.__name__}.doDragLegacy")
    
    def dragMarquee(self, event: om.MEvent):
        constants.log.debug(f"{self.__class__.__name__}.dragMarquee")
    
    def doPtrMoved(self, event: om.MEvent, draw_mgt: omr.MUIDrawManager, context: omr.MFrameContext):
        constants.log.debug(f"{self.__class__.__name__}.doPtrMoved")
        self._mouse_pos = event.position
        self._draw_circle(draw_mgt)
    
    def doPtrMovedLegacy(self, event: om.MEvent):
        constants.log.debug(f"{self.__class__.__name__}.doPtrMovedLegacy")

    def doRelease(self, event: om.MEvent, draw_mgt: omr.MUIDrawManager, context: omr.MFrameContext):
        constants.log.debug(f"{self.__class__.__name__}.doRelease")
    
    def doReleaseLegacy(self, event: om.MEvent):
        constants.log.debug(f"{self.__class__.__name__}.doReleaseLegacy")
    
    def releaseMarquee(self, event: om.MEvent):
        constants.log.debug(f"{self.__class__.__name__}.releaseMarquee")
    
    def doPressCommon(self, event: om.MEvent, draw_mgt: omr.MUIDrawManager, context: omr.MFrameContext):
        constants.log.debug(f"{self.__class__.__name__}.doPressCommon")

    def doDragCommon(self, event: om.MEvent, draw_mgt: omr.MUIDrawManager, context: omr.MFrameContext):
        constants.log.debug(f"{self.__class__.__name__}.doDragCommon")

    def doReleaseCommon(self, event: om.MEvent, draw_mgt: omr.MUIDrawManager, context: omr.MFrameContext):
        constants.log.debug(f"{self.__class__.__name__}.doReleaseCommon")
          
    def completeAction(self):
        constants.log.debug(f"{self.__class__.__name__}.completeAction")
        
    def deleteAction(self):
        constants.log.debug(f"{self.__class__.__name__}.deleteAction")
        
    def abortAction(self):
        constants.log.debug(f"{self.__class__.__name__}.abortAction")

    def reset_context(self):
        constants.log.debug(f"{self.__class__.__name__}.reset_context")
    
    def drawFeedback(self, draw_mgt: omr.MUIDrawManager, context: omr.MFrameContext):
        constants.log.debug(f"{self.__class__.__name__}.drawFeedback")
    
    def feedbackNumericalInput(self):
        constants.log.debug(f"{self.__class__.__name__}.feedbackNumericalInput")
    
    def _cursor_to_3d(self):
        view = omui.M3dView.active3dView()
        point = om.MPoint()
        vector = om.MVector()
        view.viewToWorld(self._mouse_pos[0], self._mouse_pos[1], point, vector)

        return point, vector
    
    def _draw_circle(self, draw_mgt: omr.MUIDrawManager):
        ray_source, ray_direction = self._cursor_to_3d()
        draw_mgt.circle(ray_source, ray_direction, self.radius * 1e-3, 30, False)
    
    def _get_hit_point(self) -> Optional[om.MFloatPoint]:
        ray_source, ray_direction = self._cursor_to_3d()
        intersection = self._mesh_fn.closestIntersection(om.MFloatPoint(ray_source),
                                                         om.MFloatVector(ray_direction),
                                                         om.MSpace.kWorld, 99999, False)

        return intersection[0] if intersection else None