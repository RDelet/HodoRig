from __future__ import annotations

from maya.api import OpenMaya as om, OpenMayaUI as omui, OpenMayaRender as omr

from HodoRig.Plugins.SmoothSkin.smoothSkinCtx import SmoothSkinCtx
from HodoRig.Plugins.SmoothSkin import constants


def maya_useNewAPI():
    """!@Brief Maya API 2.0"""
    pass


class SmoothWeightsContextCmd(omui.MPxContextCommand):
    
    def __init__(self):
        super().__init__()
        constants.log.debug(f"{self.__class__.__name__}.__init__")
        # self._flag = None
        
    def makeObj(self) -> SmoothSkinCtx:
        constants.log.debug(f"Make object {self.__class__.__name__}")
        return SmoothSkinCtx() 
    
    @classmethod
    def creator(cls) -> SmoothWeightsContextCmd:
        constants.log.debug(f"Create {cls.__name__}")
        return cls()

    def appendSyntax(self):
        constants.log.debug(f"{self.__class__.__name__}.appendSyntax")
        """
        syntax = self.syntax()
        syntax.addFlag(kFlag, kLongFlag, om.MSyntax.kDouble)
        """

    def doEditFlags(self):
        constants.log.debug(f"{self.__class__.__name__}.doEditFlags")
        """
        argParser = self.parser()
        if argParser.isFlagSet(kFlag):
            flag = argParser.flagArgumentInt(kFlag, 0)
            self._flag = flag
            print(f'===>>> Editing flag with value: {flag} <<<===')
        """

    def doQueryFlags(self):
        constants.log.debug(f"{self.__class__.__name__}.doQueryFlags")
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
        plugin_fn.registerContextCommand(constants.kToolNameCtx, SmoothWeightsContextCmd.creator)
    except:
        om.MGlobal.displayError(f"Failed to register context command: {constants.kToolNameCtx}")


def uninitializePlugin(obj: om.MObject):
    msg = "Remi Deletrain: remi.deletrain@gmail.com"
    plugin_fn = om.MFnPlugin(obj, msg, '1.0', "Any")
    try:
       plugin_fn.deregisterContextCommand(constants.kToolNameCtx)
    except:
        om.MGlobal.displayError(f"Failed to deregister context command: {constants.kToolNameCtx}")