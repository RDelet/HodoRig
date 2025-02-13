from maya import cmds, mel

from ...Plugins.SmoothSkin import constants


def delete_smooth_weights_ctx():
    context = f"{constants.kToolNameCtx}1"
    if cmds.contextInfo(context, query=True, exists=True):
        cmds.deleteUI(context)


def create_smooth_weights_ctx():
    context = f"{constants.kToolNameCtx}1"
    if not cmds.contextInfo(context, query=True, exists=True):
        context = mel.eval(constants.kToolNameCtx)
    cmds.setToolTo(context)
