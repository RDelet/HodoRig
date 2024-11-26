from __future__ import annotations
from typing import Optional

from ..Core import constants as cst
from .signal import Signal


class Setting(object):

    def __init__(self, name: str, value: cst.T,
                 nice_name: Optional[str] = None, default: Optional[cst.T] = None):

        self.value_changed = Signal()

        self._name = name
        self._nice_name = nice_name
        self._value = value
        self._default = default

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name: {self._name}, value: {self._value})"

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> cst.T:
        return self._value

    @value.setter
    def value(self, value: cst.T):
        if value != self._value:
            self._value = value
            self.value_changed.emit(self)
    
    @property
    def default(self) -> cst.T:
        return self._default

    @default.setter
    def default(self, value: cst.T):
        self._default = value


class Settings:

    def __init__(self):
        self._settings = dict()
        self.value_changed = Signal()

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(count: {len(self._settings)})"

    def __len__(self) -> int:
        return len(self._settings)

    def __iter__(self) -> iter:
        return ((s, v) for s, v in list(self._settings.items()))

    def add(self, setting: Setting):
        setting_name = setting.name
        setting.value_changed.register(self._value_changed)
        if setting_name in self._settings:
            raise ValueError('Setting "{}" already exists'.format(setting_name))
        self._settings[setting_name] = setting

    def exists(self, name: str) -> bool:
        return name in self._settings

    def get(self, name: str) -> Setting:
        if not self.exists(name):
            raise ValueError(f"Setting {name} does not exist")
        return self._settings[name]
    
    def set(self, name: str, value: cst.T):
        if not self.exists(name):
            raise ValueError(f"Setting {name} does not exist")
        self._settings[name].value = value

    def value(self, name: str) -> cst.T:
        return self.get(name).value

    def default_value(self, name: str) -> cst.T:
        return self.get(name).attribute.default

    def remove(self, name: str):
        if not self.exists(name):
            raise ValueError(f"Setting {name} does not exist")
        setting = self._settings[name]
        setting.value_changed.unregister(self._value_changed)
        del self._settings[name]

    def _value_changed(self, setting):
        self.value_changed.emit(setting)
