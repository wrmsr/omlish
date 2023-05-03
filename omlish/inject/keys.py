import typing as ta

from .types import Key
from .types import _KeyGen


def as_key(o: ta.Any) -> Key:
    if isinstance(o, Key):
        return o
    if isinstance(o, _KeyGen):
        return o.key()
    if isinstance(o, type):
        return Key(o)
    raise TypeError(o)
