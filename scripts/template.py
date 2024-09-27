# coding=ascii

"""
!@Brief QuickScripts template.

File Path: {s_path}

Add any help !
"""

import logging
import traceback

log = logging.getLogger('QuickScripts template')
log.setLevel(logging.INFO)

kMayaMenu = False

kCategory = None
kAnnotation = None
kImage = None
kScriptName = 'QuickScripts_Template'


def process(*args, **kwargs):
    """!@Brief Do you process here."""
    print("Hodor !")


def main():
    try:
        process()
    except Exception:
        log.error(traceback.format_exc())
