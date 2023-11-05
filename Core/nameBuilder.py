# coding=ascii

import copy
import logging
import re

from HodoRig.Core.logger import log


class NameBuilder(object):
    """!@Brief Abstract class for build node name."""

    kMirror = {'L': 'R', 'M': 'M', 'R': 'L'}
    kType = 'type'
    kSide = 'side'
    kIndex = 'index'
    kPrefix = 'prefix'
    kCoreName = 'core'
    kSuffix = 'suffix'

    kTemplate = '{type}{side}{index}{prefix}{core}{suffix}'
    kSeparator = '_'
    split_template = re.compile('\w+')

    class _NameBuilderStr(str):

        def __init__(self, *args, **kwargs):
            super(NameBuilder._NameBuilderStr, self).__init__()

        def format(self, *args, **kwargs):
            """!@Brief Override"""
            for k in [k for k in self.__get_split() if kwargs.get(k, '')][:-1]:
                kwargs[k] = '{0}{1}'.format(kwargs[k], NameBuilder.kSeparator)
            return super(NameBuilder._NameBuilderStr, self).format(*args, **kwargs)

        @staticmethod
        def __get_split():
            return NameBuilder.split_template.findall(NameBuilder.kTemplate)

    def __init__(self, **kwargs):

        self.type = kwargs.get(self.kType, '')
        self.side = kwargs.get(self.kSide, '')
        self.index = kwargs.get(self.kIndex, None)
        self.prefix = kwargs.get(self.kPrefix, '')
        self.core = kwargs.get(self.kCoreName, '')
        self.suffix = kwargs.get(self.kSuffix, '')
    
    def __str__(self) -> str:
        return self.__repr__()
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self()})"

    def __call__(self, **kwargs) -> str:
        return self.build(**kwargs)

    def __eq__(self, other: "NameBuilder") -> bool:
        if not isinstance(other, NameBuilder):
            return False
        return self() == other()

    def __ne__(self, other: "NameBuilder") -> bool:
        return not (self == other)

    def build(self, namespace: bool = True) -> str:
        if self.core is None:
            return ''

        index_str = str(self.index) if self.index is not None else ""
        return self._NameBuilderStr(self.kTemplate).format(type=self.type,
                                                           side=self.side,
                                                           index=index_str,
                                                           prefix=self.prefix,
                                                           core=self.core,
                                                           suffix=self.suffix)

    def copy(self) -> "NameBuilder":
        return copy.deepcopy(self)

    def mirror(self) -> "NameBuilder":
        if self.side is not None and self.side in self.kMirror:
            self.side = self.kMirror[self.side]

    def to_dict(self) -> dict:
        return {self.kType: self.type,
                self.kSide: self.side,
                self.kIndex: self.index,
                self.kPrefix: self.prefix,
                self.kCoreName: self.core,
                self.kSuffix: self.suffix}
