from __future__ import annotations

import logging

from maya.api import OpenMaya as om, OpenMayaUI as omui, OpenMayaRender as omr


kToolNameCtx = "SmoothWeightsContext"

log = logging.getLogger(kToolNameCtx)
log.setLevel(logging.DEBUG)


def maya_useNewAPI():
    """!@Brief Maya API 2.0"""
    pass


class SmoothWeights(omui.MPxContext):

    def __init__(self):
        super().__init__()
        log.warning(f"{self.__class__.__name__}.__init__")
        
    def toolOnSetup(self,event):
        self.reset_context()
        
    def toolOffCleanup(self):
        self.reset_context()

    def doPress(self, event: om.MEvent, drawMgr, context):
        log.warning(f"{self.__class__.__name__}.doPress")
    
    def doPressLegacy(self, event: om.MEvent):
        log.warning(f"{self.__class__.__name__}.doPressLegacy")
    
    def doEnterRegion(self, event: om.MEvent):
        log.warning(f"{self.__class__.__name__}.doEnterRegion")
    
    def doHold(self, event: om.MEvent, drawMgr, context):
        log.warning(f"{self.__class__.__name__}.doHold")
    
    def doHoldLegacy(self, event: om.MEvent):
        log.warning(f"{self.__class__.__name__}.doHoldLegacy")

    def doDrag(self, event: om.MEvent, drawMgr, context):
        log.warning(f"{self.__class__.__name__}.doDrag")
    
    def doDragLegacy(self, event: om.MEvent):
        log.warning(f"{self.__class__.__name__}.doDragLegacy")
    
    def dragMarquee(self, event: om.MEvent):
        log.warning(f"{self.__class__.__name__}.dragMarquee")
    
    def doPtrMoved(self, event: om.MEvent, drawMgr, context):
        pass
        # log.debug(f"{self.__class__.__name__}.doPtrMoved")
    
    def doPtrMovedLegacy(self, event: om.MEvent):
        log.warning(f"{self.__class__.__name__}.doPtrMovedLegacy")

    def doRelease(self, event: om.MEvent, drawMgr, context):
        log.warning(f"{self.__class__.__name__}.doRelease")
    
    def doReleaseLegacy(self, event: om.MEvent):
        log.warning(f"{self.__class__.__name__}.doReleaseLegacy")
    
    def releaseMarquee(self, event: om.MEvent):
        log.warning(f"{self.__class__.__name__}.releaseMarquee")
    
    def doPressCommon(self, event: om.MEvent, drawMgr, context):
        log.warning(f"{self.__class__.__name__}.doPressCommon")

    def doDragCommon(self, event: om.MEvent, drawMgr, context):
        log.warning(f"{self.__class__.__name__}.doDragCommon")

    def doReleaseCommon(self, event: om.MEvent, drawMgr, context):
        log.warning(f"{self.__class__.__name__}.doReleaseCommon")
          
    def completeAction(self):
        log.warning(f"{self.__class__.__name__}.completeAction")
        
    def deleteAction(self):
        log.warning(f"{self.__class__.__name__}.deleteAction")
        
    def abortAction(self):
        log.warning(f"{self.__class__.__name__}.abortAction")

    def reset_context(self):
        log.warning(f"{self.__class__.__name__}.reset_context")
    
    def drawFeedback(self, draw_manager: omui.MUIDrawManager, frame_context: omr.MFrameContext):
        pass
        # log.debug(f"{self.__class__.__name__}.drawFeedback")
    
    def feedbackNumericalInput(self):
        log.warning(f"{self.__class__.__name__}.feedbackNumericalInput")


class SmoothWeightsContextCmd(omui.MPxContextCommand):
    
    def __init__(self):
        super().__init__()
        log.warning(f"{self.__class__.__name__}.__init__")
        # self._flag = None
        
    def makeObj(self) -> SmoothWeights:
        log.warning(f"Make object {self.__class__.__name__}")
        return SmoothWeights() 
    
    @classmethod
    def creator(cls) -> SmoothWeightsContextCmd:
        log.warning(f"Create {cls.__name__}")
        return cls()

    def appendSyntax(self):
        log.warning(f"{self.__class__.__name__}.appendSyntax")
        """
        syntax = self.syntax()
        syntax.addFlag(kFlag, kLongFlag, om.MSyntax.kDouble)
        """

    def doEditFlags(self):
        log.warning(f"{self.__class__.__name__}.doEditFlags")
        """
        argParser = self.parser()
        if argParser.isFlagSet(kFlag):
            flag = argParser.flagArgumentInt(kFlag, 0)
            self._flag = flag
            print(f'===>>> Editing flag with value: {flag} <<<===')
        """

    def doQueryFlags(self):
        log.warning(f"{self.__class__.__name__}.doQueryFlags")
        """
        argParser = self.parser()
        if argParser.isFlagSet(kFlag):
            if hasattr(self, 'flag'):
                print(f'===>>> Querying flag {kLongFlag}: {self._flag} <<<===')
                self.setResult(self._flag)
        """


def initializePlugin(obj: om.MObject):
    
    msg = "Remi Deletrain: remi.deletrain@gmail.com"
    plugin_fn = om.MFnPlugin(obj, msg, '1.0', "Any")
    try:
        plugin_fn.registerContextCommand(kToolNameCtx,
                                         SmoothWeightsContextCmd.creator)
    except:
        om.MGlobal.displayError(f"Failed to register context command: {kToolNameCtx}")


def uninitializePlugin(obj: om.MObject):

    msg = "Remi Deletrain: remi.deletrain@gmail.com"
    plugin_fn = om.MFnPlugin(obj, msg, '1.0', "Any")
    try:
       plugin_fn.deregisterContextCommand(kToolNameCtx)
    except:
        om.MGlobal.displayError(f"Failed to deregister context command: {kToolNameCtx}")