import collections.abc
from inspect import ismethod
from typing import Callable, TypeVar
import weakref


T = TypeVar("T")  # pylint: disable = invalid-name


class Signal:

    def __init__(self):
        self._callbacks = []
        self.lock = False
    
    def __str__(self) -> str:
        return self.__repr__()
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(count: {len(self._callbacks)})"
    
    def __wrap_weakref(self, slot: Callable[[T], None]) -> weakref.ReferenceType:
        return weakref.WeakMethod(slot) if ismethod(slot) else weakref.ref(slot)
    
    @property
    def registered(self) -> list:
        return [x() for x in self._callbacks]

    def register(self, slot: Callable[[T], None]) -> None:
        if not isinstance(slot, collections.abc.Callable):
            raise ValueError("Argument must be callable")
        
        if slot not in self.registered:
            ref = self.__wrap_weakref(slot)
            self._callbacks.append(ref)

    def unregister(self, slot: Callable[[T], None]) -> None:
        if not isinstance(slot, collections.abc.Callable):
            raise ValueError("Argument must be callable")
        
        registered = self.registered
        if slot in registered:
            slot_id = registered.index(slot)
            self._callbacks.remove(self._callbacks[slot_id])

    def emit(self, *args: T) -> None:
        if not self.lock:
            for slot in self._callbacks:
                slot()(*args)