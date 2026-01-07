from functools import partial
from pathlib import Path
import traceback

from PySide2 import QtCore

from maya import cmds

from .Core.logger import log
from . import Components  # Initialise all components for node class


_current_dir = Path(__file__).parent
batch_mode = cmds.about(batch=True)


"""
try:
    from .Core import _install_lib
    _install_lib.install()
except Exception as exp:
    log.debug(traceback.format_exc())
    log.error("Error on install external lib !")
"""

try:
    from .Core import apiUndo
    apiUndo.install()
except Exception:
    log.debug(traceback.format_exc())
    log.error("Error on install apiUndo !")   


try:
    from .Helpers import quickScripts
    quickScripts.retrieve()
except Exception:
    log.debug(traceback.format_exc())
    log.error("Error on install HodoRig scripts !")


try:
    from .Ui.Overrides.mayaMenu import build_hodorig_menu
    cmds.evalDeferred(build_hodorig_menu)
except Exception:
    log.debug(traceback.format_exc())
    log.error("Error on create HodoRig menu !")


try:
    from .Helpers.hotKey import Hotkey
    file_path = _current_dir / "Settings" / "hotKeys.json"
    cmds.evalDeferred(partial(Hotkey.from_file, file_path))
except Exception as exp:
    log.debug(traceback.format_exc())
    log.error("Error on install HodoRig HotKey !")


try:
    plugins = ["quatNodes", "lookdevKit"]
    for plugin in plugins:
        if not cmds.pluginInfo(plugin, query=True, loaded=True):
            log.debug(f"Load plugin {plugin}")
            cmds.loadPlugin(plugin)
except Exception as exp:
    log.debug(traceback.format_exc())
    log.error("Error on load plugin !")       


def _install_highlighter(timer: QtCore.QTimer, next_timer: QtCore.QTimer):
    if mayaScriptEditor.install_highlighter():
        timer.stop()
        cmds.evalDeferred(partial(next_timer.start, 200))

def _install_linker(timer: QtCore.QTimer):
    if mayaScriptEditor.install_linker():
        timer.stop()
        

try:
    if not batch_mode and cmds.about(version=True) < "2025":
        from .Ui.Overrides import mayaScriptEditor
        # Pour niquer le evaldeffered qui ne fonctionne pas...
        ttimer = QtCore.QTimer()
        ttimer.timeout.connect(partial(_install_linker, ttimer))
        timer = QtCore.QTimer()
        timer.timeout.connect(partial(_install_highlighter, timer, ttimer))
        cmds.evalDeferred(partial(timer.start, 200))
except Exception:
    log.debug(traceback.format_exc())
    log.error("Error on create highlither !")