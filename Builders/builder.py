import os
import traceback

from HodoRig.Core import file
from HodoRig.Core.context import NodeCacheContext
from HodoRig.Core.logger import log
from HodoRig.Core.cache import NodeCache


class Builder(object):

    kFiledirectory = None
    kFileExtension = None

    def __init__(self):
        self._file_path = None
        self._data = []
        self._node_cache = NodeCache(enable=False)

    def __str__(self) -> str:
        return self.__repr__()
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}"

    @property
    def file_path(self) -> str:
        return self._file_path

    @property
    def data(self) -> list:
        return self._data

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

    @classmethod
    def load(cls, file_path: str, *args, **kwargs):
        new_cls = cls(*args, **kwargs)
        new_cls._file_path = file_path
        new_cls._data = file.read_json(new_cls._file_path)

        return new_cls

    def dump(self, output_path: str):
        if not self._data:
            raise RuntimeError(f"{self.__class__.__name__} data is empty !")
        file.dump_json(self._data, output_path)
        log.info(f"File write: {output_path}")
