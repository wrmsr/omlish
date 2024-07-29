import inspect
import typing as ta

from .. import dataclasses as dc
from .. import lang


T = ta.TypeVar('T')


##


class Multi(lang.Abstract, lang.Sealed):
    pass


class SetMulti(Multi, lang.Singleton, lang.Final):
    pass


@dc.dataclass(frozen=True)
@dc.extra_params(cache_hash=True)
class MapMulti(Multi, lang.Final):
    key: ta.Any


##


@dc.dataclass(frozen=True)
@dc.extra_params(cache_hash=True)
class Key(lang.Final, ta.Generic[T]):
    cls: type[T] | ta.NewType
    tag: ta.Any = dc.field(default=None, kw_only=True)
    multi: Multi | None = dc.field(default=None, kw_only=True)


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


def set_multi(o: ta.Any) -> Key:
    return dc.replace(as_key(o), multi=SetMulti())


def map_multi(k: ta.Any, o: ta.Any) -> Key:
    return dc.replace(as_key(o), multi=MapMulti(k))


def tag(o: ta.Any, t: ta.Any) -> Key:
    return dc.replace(as_key(o), tag=t)
