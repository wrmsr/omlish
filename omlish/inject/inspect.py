import typing as ta

from .. import lang
from .keys import Key
from .keys import as_key


if ta.TYPE_CHECKING:
    from .impl import inspect as _inspect
else:
    _inspect = lang.proxy_import('.impl.inspect', __package__)


T = ta.TypeVar('T')


##


class Kwarg(ta.NamedTuple):
    name: str
    key: Key
    has_default: bool

    @classmethod
    def of(
            cls,
            name: str,
            key: Key,
            *,
            has_default: bool = False,
    ) -> 'Kwarg':
        return cls(
            name,
            key,
            has_default,
        )


class KwargsTarget(ta.NamedTuple):
    obj: ta.Any
    kwargs: ta.Sequence[Kwarg]

    @classmethod
    def of(
            cls,
            obj: ta.Any,
            *kws: Kwarg,
            **kwargs: tuple[Key, bool] | Key | ta.Any,
    ) -> 'KwargsTarget':
        kw_kwargs: list[Kwarg] = []
        for n, v in kwargs.items():
            if isinstance(v, tuple):
                kw_k, kw_hd = v
                kw_kwargs.append(Kwarg.of(n, kw_k, has_default=kw_hd))
            else:
                kw_kwargs.append(Kwarg.of(n, as_key(v)))

        return cls(
            obj,
            [*kws, *kw_kwargs],
        )


def tag(obj: T, **kwargs: ta.Any) -> T:
    return _inspect.tag(obj, **kwargs)


def build_kwargs_target(obj: ta.Any, **kwargs: ta.Any) -> KwargsTarget:
    return _inspect.build_kwargs_target(obj, **kwargs)
