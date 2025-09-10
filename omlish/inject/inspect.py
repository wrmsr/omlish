import typing as ta

from .. import lang
from .keys import Key


with lang.auto_proxy_import(globals()):
    from .impl import inspect as _inspect


T = ta.TypeVar('T')


##


class Kwarg(ta.NamedTuple):
    name: str
    key: Key
    has_default: bool


class KwargsTarget(ta.NamedTuple):
    obj: ta.Any
    kwargs: ta.Sequence[Kwarg]


def tag(obj: T, **kwargs: ta.Any) -> T:
    return _inspect.tag(obj, **kwargs)


def build_kwargs_target(obj: ta.Any, **kwargs: ta.Any) -> KwargsTarget:
    return _inspect.build_kwargs_target(obj, **kwargs)
