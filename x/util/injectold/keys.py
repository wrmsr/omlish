import inspect
import typing as ta

from .. import dataclasses as dc
from .types import Key
from .types import _KeyGen


##


def as_key(o: ta.Any) -> Key:
    if o is inspect.Parameter.empty:
        raise TypeError(o)
    if isinstance(o, Key):
        return o
    if isinstance(o, _KeyGen):
        return o._gen_key()  # noqa
    if isinstance(o, type):
        return Key(o)
    raise TypeError(o)


##


def array(o: ta.Any) -> Key:
    return dc.replace(as_key(o), arr=True)


def tag(o: ta.Any, t: ta.Any) -> Key:
    return dc.replace(as_key(o), tag=t)
