import traceback

from HodoRig.Core.logger import log
from HodoRig.Core.cache import NodeCache
from HodoRig.Core.context import NodeCacheContext


class Builder(object):

    def __init__(self):
        self._node_cache = NodeCache(enable=False)

    def __str__(self) -> str:
        return self.__repr__()
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}"

    def _pre_build(self, *args, **kwargs):
        log.debug(f"{self.__class__.__name__} pre build !")

    def _build(self, *args, **kwargs):
        log.debug(f"{self.__class__.__name__} build !")

    def _post_build(self, *args, **kwargs):
        log.debug(f"{self.__class__.__name__} post build !")

    def build(self, *args, **kwargs):

        with NodeCacheContext(self._node_cache):
            try:
                self._pre_build(*args, **kwargs)
            except Exception:
                self._on_build_failed()
                raise RuntimeError("Error on pre build !")
            
            try:
                self._build(*args, **kwargs)
            except Exception:
                self._on_build_failed()
                raise RuntimeError("Error on pre build !")
            
            try:
                self._post_build(*args, **kwargs)
            except Exception:
                self._on_build_failed()
                raise RuntimeError("Error on pre build !")
            
            self._on_build_succed()

    def _on_build_succed(self):
        log.debug(f"{self.__class__.__name__} build succes !")

    def _on_build_failed(self):
        log.error(f"{self.__class__.__name__} build failed !")
        log.debug(traceback.format_exc())