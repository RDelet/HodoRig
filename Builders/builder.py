from ..Core.logger import log
from ..Core.cache import NodeCache
from ..Core.context import NodeCacheContext
from ..Core.signal import Signal


class Builder:

    build_succed = Signal()
    build_failed = Signal()

    def __init__(self):
        self._node_cache = NodeCache(enable=False)

    def __str__(self) -> str:
        return self.__repr__()
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}"

    def _check_validity(self):
        pass

    def _pre_build(self, *args, **kwargs):
        log.debug(f"{self.__class__.__name__} pre build !")
        self._check_validity()

    def _build(self, *args, **kwargs):
        log.debug(f"{self.__class__.__name__} build !")

    def _post_build(self, *args, **kwargs):
        log.debug(f"{self.__class__.__name__} post build !")
    
    def _on_build_succed(self):
        log.debug(f"{self.__class__.__name__} build succes !")
        self.build_succed.emit(self)

    def _on_build_failed(self):
        log.error(f"{self.__class__.__name__} build failed !")
        self.build_failed.emit(self)

    def build(self, *args, **kwargs):

        with NodeCacheContext(self._node_cache):
            try:
                self._pre_build(*args, **kwargs)
            except Exception as e:
                self._on_build_failed()
                raise RuntimeError("Error on pre build !") from e
            
            try:
                self._build(*args, **kwargs)
            except Exception as e:
                self._on_build_failed()
                raise RuntimeError("Error on build !") from e
            
            try:
                self._post_build(*args, **kwargs)
            except Exception as e:
                self._on_build_failed()
                raise RuntimeError("Error on post build !") from e
            
            self._on_build_succed()
