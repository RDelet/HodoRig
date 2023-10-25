import traceback

from PySide2 import QtWidgets

from HodoRig.Core.logger import log
from HodoRig.Ui.mayaSyntaxHighLigther import MayaSyntaxHighLigther


try:
    app = QtWidgets.QApplication.instance()
    app.focusChanged.connect(MayaSyntaxHighLigther.focus_changed_cb)
    MayaSyntaxHighLigther.add_on_all_control()
except Exception:
    log.debug(traceback.format_exc())
    log.error("Error on create high lither syntax !")
