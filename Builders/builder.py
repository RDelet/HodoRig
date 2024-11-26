from __future__ import annotations

from ..Core.logger import log
from ..Core.nameBuilder import NameBuilder
from ..Core.cache import NodeCache
from ..Core.context import NodeCacheContext
from ..Core.settings import Settings
from ..Core.signal import Signal
from .builderState import BuilderState


class Builder:

    build_succed = Signal()
    build_failed = Signal()

    def __init__(self, name: str | NameBuilder):
        self._name = name if isinstance(name, NameBuilder) else NameBuilder.from_name(name)
        self._node_cache = NodeCache(enable=False)
        self._state = BuilderState()
        self._settings = Settings()

        self._init_settings()

    def __str__(self) -> str:
        return self.__repr__()
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}"
    
    def _init_settings(self):
        pass

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
            except Exception as err:
                self._on_build_failed()
                log.error("Error on pre build !")
                raise err
            
            try:
                self._build(*args, **kwargs)
            except Exception as err:
                self._on_build_failed()
                log.error("Error on build !")
                raise err
            
            try:
                self._post_build(*args, **kwargs)
            except Exception as err:
                self._on_build_failed()
                log.error("Error on post build !")
                raise err
            
            self._on_build_succed()
    
    @property
    def name(self) -> NameBuilder:
        return self._name
    
    @name.setter
    def name(self, name: str | NameBuilder):
        self._name = name if isinstance(name, NameBuilder) else NameBuilder.from_name(name)

    @property
    def settings(self):
        return self._settings
    
    @property
    def state(self) -> BuilderState:
        return self._state
