import inspect
import typing as ta

from .. import dataclasses as dc
from .types import Key


##


def as_key(o: ta.Any) -> Key:
    if o is inspect.Parameter.empty:
        raise TypeError(o)
    if isinstance(o, Key):
        return o
    if isinstance(o, (type, ta.NewType)):  # noqa
        return Key(o)
    raise TypeError(o)


##


def multi(o: ta.Any) -> Key:
    return dc.replace(as_key(o), multi=True)


def tag(o: ta.Any, t: ta.Any) -> Key:
    return dc.replace(as_key(o), tag=t)
