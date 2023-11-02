import logging
import sys
import types

from maya import cmds
from maya.api import OpenMaya


__version__ = "0.6.2"

log = logging.getLogger("Api Undo")

# Support for multiple co-existing versions of apiundo.
unique_command = f'apiUndo_{__version__.replace(".", "_")}_command'

# This module is both a Python module and Maya plug-in.
# Data is shared amongst the two through this "module"
unique_shared = f'apiUndo_{__version__.replace(".", "_")}_shared'
if unique_shared not in sys.modules:
    sys.modules[unique_shared] = types.ModuleType(unique_shared)

self = sys.modules[__name__]
self.installed = False

shared = sys.modules[unique_shared]
shared.undoId = None
shared.redoId = None
shared.undos = {}
shared.redos = {}


# noinspection PyPep8Naming
def maya_useNewAPI():
    """!@Brief Plug-in boilerplate"""
    pass


def clear():
    """!@Brief Clear all memory used by cmdx, including undo
               Traces left in here can trick Maya into thinking
               nodes still exists that cannot be unloaded.
    """
    self.shared.undoId = None
    self.shared.redoId = None
    self.shared.undos = {}
    self.shared.redos = {}
    cmds.flushUndo()


def commit(undo, redo=lambda: None):
    """!@Brief Commit undo and redo to history.

    @type undo: func
    @param undo: Call this function on next undo
    @type redo: func / None
    @param redo: Like `undo`, for for redo
    """
    if not hasattr(cmds, unique_command):
        install()
    # Precautionary measure.
    # If this doesn't pass, odds are we've got a race condition.
    # NOTE: This assumes calls to `commit` can only be done
    # from a single thread, which should already be the case
    # given that Maya's API is not threadsafe.
    try:
        assert shared.redoId is None
        assert shared.undoId is None
    except AssertionError:
        log.debug("%s has a problem with undo" % __name__)
    # Temporarily store the functions at shared-level,
    # they are later picked up by the command once called.
    shared.undoId = "%x" % id(undo)
    shared.redoId = "%x" % id(redo)
    shared.undos[shared.undoId] = undo
    shared.redos[shared.redoId] = redo
    # Let Maya know that something is undoable
    getattr(cmds, unique_command)()


def install():
    """!@Brief Load this module as a plug-in
               Source: https://github.com/mottosso/cmdx/blob/master/cmdx.py
    """
    cmds.loadPlugin(__file__, quiet=True)
    self.installed = True


def uninstall():
    """!@Brief Plug-in may exist in undo queue and
               therefore cannot be unloaded until flushed.
    """
    clear()
    cmds.unloadPlugin(__file__)
    self.installed = False


# noinspection PyPep8Naming
class _apiUndo(OpenMaya.MPxCommand):
    # For debugging, should always be 0 unless there's something to undo
    _aliveCount = 0

    def __init__(self, *args, **kwargs):
        super(_apiUndo, self).__init__(*args, **kwargs)

        _apiUndo._aliveCount += 1
        self.undoId = None
        self.redoId = None

    def __del__(self):
        _apiUndo._aliveCount -= 1
        # Relive whatever was held in memory
        # This *should* always contain the undo ID
        # of the current command instance. If it doesn't,
        # the `shared` module must have been either
        # edited or deleted outside of cmdx, such as
        # if the module was reloaded.
        #
        # However, we can't afford throwing errors here,
        # and errors here isn't a big whop anyway since they
        # would be deleted and cleaned up on unloading
        # of the `cmdx` module along with the `shared`
        # instance from sys.module. E.g. on Maya restart.
        shared.undos.pop(self.undoId, None)
        shared.redos.pop(self.redoId, None)
        self.undoId = None
        self.redoId = None

    # noinspection PyPep8Naming
    def doIt(self, args):
        # Store the last undo/redo commands in this
        # instance of the _apiUndo command.
        self.undoId = shared.undoId
        self.redoId = shared.redoId
        # With that stored, let's avoid storing it elsewhere
        shared.undoId = None
        shared.redoId = None

    # noinspection PyPep8Naming
    def undoIt(self):
        # If the undo ID does not exist, it means
        # we've erased commands still active in the undo
        # queue, which isn't good. E.g. the cmdx module
        # was reloaded.
        shared.undos[self.undoId]()

    # noinspection PyPep8Naming
    def redoIt(self):
        shared.redos[self.redoId]()

    # noinspection PyPep8Naming
    def isUndoable(self):
        # Without this, the above undoIt and redoIt will not be called
        return True


# noinspection PyPep8Naming
def initializePlugin(plugin):
    """!@Brief Plug-in boilerplate"""
    OpenMaya.MFnPlugin(plugin).registerCommand(unique_command, _apiUndo)


# noinspection PyPep8Naming
def uninitializePlugin(plugin):
    """!@Brief Plug-in boilerplate"""
    OpenMaya.MFnPlugin(plugin).deregisterCommand(unique_command)
