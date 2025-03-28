from contextlib import contextmanager

from maya import cmds

from ..Helpers import utils
from ..Core.cache import NodeCache


class Context:

    def __init__(self, *args, **kwargs):
        pass

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"MasterOfPuppet(class: {self.__class__.__name__})"

    def __enter__(self, *args, **kwargs):
        raise NotImplementedError('{0}.__enter__ need to be reimplemented !'.format(self.__class__.__name__))

    def __exit__(self, *args, **kwargs):
        raise NotImplementedError('{0}.__exit__ need to be reimplemented !'.format(self.__class__.__name__))


class NodeCacheContext(Context):

    def __init__(self, cache: NodeCache, clear: bool = True):
        super().__init__()
        self._cache = cache
        self._clear = clear

    def __enter__(self):
        if self._clear:
            self._cache.clear()
        self._cache.enable = True
        utils.node_caches.append(self._cache)

    def __exit__(self, *args, **kwargs):
        self._cache.enable = False
        del utils.node_caches[utils.node_caches.index(self._cache)]


@contextmanager
def KeepSelection():
    selection = cmds.ls(selection=True, long=True)
    try:
        yield selection
    finally:
        cmds.select(selection)
