from functools import partial
from pathlib import Path
import traceback

try:
    from PySide2 import QtWidgets
except:
    from PySide6 import QtWidgets

from maya import cmds

from .Core.logger import log


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
    if not batch_mode:
        from .Ui.Overrides.mayaSyntaxHighLigther import MayaSyntaxHighLigther
        app = QtWidgets.QApplication.instance()
        app.focusChanged.connect(MayaSyntaxHighLigther.focus_changed_cb)
        MayaSyntaxHighLigther.add_on_all_control()
except Exception:
    log.debug(traceback.format_exc())
    log.error("Error on create high lither syntax !")


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
    func = partial(Hotkey.from_file, file_path)
    cmds.evalDeferred(func)
except Exception as exp:
    log.debug(traceback.format_exc())
    log.error("Error on install HodoRig HotKey !")


try:
    plugins = ["quatNodes", "lokkDevKit"]
    for plugin in plugins:
        if not cmds.pluginInfo(plugin, query=True, loaded=True):
            log.debug(f"Load plugin {plugin}")
            cmds.loadPlugin(plugin)
except Exception as exp:
    log.debug(traceback.format_exc())
    log.error("Error on load plugin !")       
