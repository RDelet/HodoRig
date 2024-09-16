from functools import partial
import os
import traceback

from PySide2 import QtWidgets

from maya import cmds

from .Core.logger import log


dir, _ = os.path.split(__file__)

try:
    batch_mode = cmds.about(batch=True)
except Exception:
    batch_mode = True


try:
    from .Core import apiUndo

    apiUndo.install()
except Exception:
    log.error(traceback.format_exc())
    log.error("Error on install apiUndo !")   


try:
    if not batch_mode:
        from .Ui.Overrides.mayaSyntaxHighLigther import MayaSyntaxHighLigther

        app = QtWidgets.QApplication.instance()
        app.focusChanged.connect(MayaSyntaxHighLigther.focus_changed_cb)
        MayaSyntaxHighLigther.add_on_all_control()
except Exception:
    log.info(traceback.format_exc())
    log.error("Error on create high lither syntax !")


try:
    from .Core import quickScripts

    hodorig_scripts = os.path.normpath(os.path.join(dir, "scripts"))
    quickScripts.register_path(hodorig_scripts)
    quickScripts.retrieve()
except Exception:
    log.info(traceback.format_exc())
    log.error("Error on install HodoRig scripts !")


try:
    from .Core import quickScripts
    from .Ui.Overrides.mayaMenu import MenuItem, Item

    _sub_menu = {}

    def __build_sub_menu(menu_name: str, parent: MenuItem = None):
        if not menu_name:
            return

        sub_menu = None
        if menu_name in _sub_menu:
            sub_menu = _sub_menu[menu_name]
        else:
            sub_menu = Item(menu_name, annotation="")
            _sub_menu[menu_name] = sub_menu
            if parent:
                parent.add_item(sub_menu)

        return sub_menu

    def create_from_scripts():
        main_menu = MenuItem("HodoRig", annotation="HodoRig Tools")
        scripts = quickScripts.get_scripts()
        for name, mod in scripts.items():
            if not mod.kMayaMenu:
                continue
            sub_menu = __build_sub_menu(mod.kCategory, parent=main_menu)
            item = Item(name, annotation=mod.kAnnotation, image=mod.kImage,
                        command=mod.main)
            sub_menu.add_item(item) if sub_menu else main_menu.add_item(item)
        main_menu.create()
    cmds.evalDeferred(create_from_scripts)
except Exception:
    log.info(traceback.format_exc())
    log.error("Error on create HodoRig menu !")


try:
    from .Core.hotKey import Hotkey

    file_path = os.path.normpath(os.path.join(dir, "Settings/hotKeys.json"))
    func = partial(Hotkey.from_file, file_path)
    cmds.evalDeferred(func)
except Exception as exp:
    log.info(traceback.format_exc())
    log.error("Error on install HodoRig HotKey !")