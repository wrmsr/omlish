import threading
import typing as ta

from .base import Codec


##


class CodecRegistry:
    def __init__(self) -> None:
        super().__init__()

        self._lock = threading.RLock()
        self._lst: list[Codec] = []
        self._by_name: dict[str, Codec] = {}
        self._by_cls: dict[type, list[Codec]] = {}

    def register(self, *codecs: Codec) -> ta.Self:
        with self._lock:
            for codec in codecs:
                names = {codec.name, *(codec.aliases or [])}
                for n in names:
                    if n in self._by_name:
                        raise KeyError(n)

            for codec in codecs:
                self._lst.append(codec)
                for n in names:
                    self._by_name[n] = codec
                for t in type(codec).__mro__:
                    if t is not object:
                        self._by_cls.setdefault(t, []).append(codec)

        return self

    def lookup(self, name: str) -> Codec:
        with self._lock:
            return self._by_name[name]

    def lookup_type(self, cls: type) -> list[Codec]:
        with self._lock:
            return self._by_cls.get(cls, [])


##


REGISTRY = CodecRegistry()

register = REGISTRY.register
lookup = REGISTRY.lookup
