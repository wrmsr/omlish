import ast
import collections
import functools
import types
import typing as ta

from ... import check


T = ta.TypeVar('T')

K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


def repr_round_trip_value(v: T) -> T:
    r = repr(v)
    v2 = ast.literal_eval(r)
    if v != v2:
        raise ValueError(v)
    return v2


##


def set_qualname(cls: type, value: T) -> T:
    if isinstance(value, types.FunctionType):
        value.__qualname__ = f'{cls.__qualname__}.{value.__name__}'
    return value


def set_new_attribute(cls: type, name: str, value: ta.Any) -> bool:
    if name in cls.__dict__:
        return True
    set_qualname(cls, value)
    setattr(cls, name, value)
    return False


##


class SealableRegistry(ta.Generic[K, V]):
    def __init__(self) -> None:
        super().__init__()

        self._dct: dict[K, V] = {}
        self._sealed = False

    def seal(self) -> None:
        self._sealed = True

    def __setitem__(self, k: K, v: V) -> None:
        check.state(not self._sealed)
        check.not_in(k, self._dct)
        self._dct[k] = v

    def __getitem__(self, k: K) -> V:
        self.seal()
        return self._dct[k]

    def items(self) -> ta.Iterator[tuple[K, V]]:
        self.seal()
        return iter(self._dct.items())


##


def class_decorator(fn):
    @functools.wraps(fn)
    def inner(cls=None, *args, **kwargs):
        if cls is None:
            return lambda cls: fn(cls, *args, _kwargs=kwargs, **kwargs)  # noqa
        return fn(cls, *args, **kwargs)
    return inner


##


_EMPTY_MAPPING_PROXY: ta.Mapping = types.MappingProxyType({})


def chain_mapping_proxy(*ms: ta.Mapping) -> types.MappingProxyType:
    m: ta.Any
    if len(ms) > 1:
        m = collections.ChainMap(*ms)  # type: ignore[arg-type]
    elif ms:
        [m] = ms
    else:
        m = _EMPTY_MAPPING_PROXY

    return types.MappingProxyType(m)
