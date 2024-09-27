# coding=ascii

"""
!@Brief Open shape editor.

File Path: {s_path}
"""

import logging
import traceback

from ..Core.logger import log
from ..Ui.shapeBasicUI import ShapeBasicUI


log = logging.getLogger('Shape Editor')
log.setLevel(logging.INFO)

kMayaMenu = True

kCategory = None
kAnnotation = "Open shape editor UI"
kImage = None
kScriptName = 'Shape Editor'


def main():
    try:
        w = ShapeBasicUI()
        w.show()
    except Exception:
        log.error(traceback.format_exc())
