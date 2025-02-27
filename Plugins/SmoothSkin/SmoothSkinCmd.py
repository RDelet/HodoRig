from maya import cmds, mel

from ...Plugins.SmoothSkin import constants
from .smoothSkinUi import SmoothSkinUi


def delete_smooth_weights_ctx():
    context = f"{constants.kToolNameCtx}1"
    if cmds.contextInfo(context, query=True, exists=True):
        cmds.deleteUI(context)


def create_smooth_weights_ctx():
    context = f"{constants.kToolNameCtx}1"
    if not cmds.contextInfo(context, query=True, exists=True):
        context = mel.eval(constants.kToolNameCtx)
    cmds.setToolTo(context)


"""
from maya import cmds

from HodoRig.Plugins.SmoothSkin import smoothSkinUi
from HodoRig.Plugins.SmoothSkin import smoothSkinCmd


plugin_path = r"D:\Work\GitHub\HodoRig\Plugins\SmoothSkin\smoothSkinPlugin.py"
if not cmds.pluginInfo(plugin_path, query=True, loaded=True):
    cmds.loadPlugin(plugin_path)

smoothSkinCmd.delete_smooth_weights_ctx()
smoothSkinCmd.create_smooth_weights_ctx()

pouet = smoothSkinUi.SmoothSkinUi()
pouet.show()
"""