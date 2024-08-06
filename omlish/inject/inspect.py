import typing as ta

from .. import lang
from .keys import Key


if ta.TYPE_CHECKING:
    from .impl import inspect as _inspect
else:
    _inspect = lang.proxy_import('.impl.inspect', __package__)


T = ta.TypeVar('T')


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
