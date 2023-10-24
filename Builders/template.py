from typing import Union

from maya.api import OpenMaya

from HodoRig.Core import constants, file
from HodoRig.Core.logger import log
from HodoRig.Builders.builder import Builder


class Template(Builder):

    kFiledirectory = constants.kShapeDir
    kFileExtension = constants.kShapeExtension

    def __init__(self, template_name: str):
        super().__init__()
        self._file_path = self.build_path(template_name)
        self._data = file.read_json(self._file_path)

    def _pre_build(self, *args, **kwargs):
        log.debug(f"{self.__class__.__name__} pre build: {self._file_path} !")

    def _build(self, *args, **kwargs):
        log.debug(f"{self.__class__.__name__} build: {self._file_path} !")

    def _post_build(self, *args, **kwargs):
        log.debug(f"{self.__class__.__name__} post build: {self._file_path} !")