from typing import Callable, TypeVar


T = TypeVar("T")  # pylint: disable = invalid-name


class Signal:

    def __init__(self):
        self._callbacks = []
        self.lock = False
    
    def __str__(self) -> str:
        return self.__repr__()
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(count: {len(self._callbacks)})"
    
    @property
    def registered(self) -> list:
        return self._callbacks

    def register(self, callback: Callable[[T], None]) -> None:
        if callback not in self._callbacks:
            self._callbacks.append(callback)

    def unsubscribe(self, callback: Callable[[T], None]) -> None:
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def emit(self, *args: T) -> None:
        if not self.lock:
            for callback in self._callbacks:
                callback(*args)
