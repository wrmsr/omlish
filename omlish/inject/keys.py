import inspect
import typing as ta

from .. import dataclasses as dc
from .. import lang
from .. import reflect as rfl


T = ta.TypeVar('T')


##


@dc.dataclass(frozen=True)
@dc.extra_params(cache_hash=True)
class Key(lang.Final, ta.Generic[T]):
    ty: rfl.Type = dc.xfield(coerce=rfl.type_)
    tag: ta.Any = dc.field(default=None, kw_only=True)


##


def as_key(o: ta.Any) -> Key:
    if o is inspect.Parameter.empty:
        raise TypeError(o)
    if isinstance(o, Key):
        return o
    return Key(rfl.type_(o))


##


def tag(o: ta.Any, t: ta.Any) -> Key:
    return dc.replace(as_key(o), tag=t)
