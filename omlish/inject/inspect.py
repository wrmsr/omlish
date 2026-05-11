import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import lang
from .keys import Key
from .keys import as_key


if ta.TYPE_CHECKING:
    from .impl import inspect as _inspect
else:
    _inspect = lang.proxy_import('.impl.inspect', __package__)


T = ta.TypeVar('T')


##


@dc.dataclass(frozen=True)
@dc.extra_class_params(cache_hash=True, terse_repr=True)
class Kwarg(lang.Final):
    name: str
    key: Key

    _: dc.KW_ONLY

    has_default: bool = False

    def __post_init__(self) -> None:
        check.isinstance(self.key, Key)
        check.non_empty_str(self.name)

    @classmethod
    def seq_of(
            cls,
            *kws: Kwarg,
            **kwargs: tuple[Key | ta.Any, bool] | Key | ta.Any,
    ) -> ta.Sequence[Kwarg]:
        lst: list[Kwarg] = list(kws)
        for n, v in kwargs.items():
            if isinstance(v, tuple):
                kw_k, kw_hd = v
                lst.append(Kwarg(n, as_key(kw_k), has_default=kw_hd))
            else:
                lst.append(Kwarg(n, as_key(v)))
        return tuple(lst)


@dc.dataclass(frozen=True)
@dc.extra_class_params(cache_hash=True, terse_repr=True)
class KwargsTarget(lang.Final):
    obj: ta.Any
    kwargs: ta.Sequence[Kwarg] = dc.xfield(coerce=tuple)

    def override(
            self,
            *kws: Kwarg,
            **kwargs: tuple[Key | ta.Any, bool] | Key | ta.Any,
    ) -> KwargsTarget:
        new_kws: dict[str, Kwarg] = {kw.name: kw for kw in self.kwargs}
        for kw in Kwarg.seq_of(*kws, **kwargs):
            new_kws[kw.name] = kw
        return KwargsTarget(self.obj, tuple(new_kws.values()))

    @classmethod
    def of(
            cls,
            obj: ta.Any,
            *kws: Kwarg,
            **kwargs: tuple[Key | ta.Any, bool] | Key | ta.Any,
    ) -> KwargsTarget:
        return cls(obj, Kwarg.seq_of(*kws, **kwargs))


def tag(obj: T, **kwargs: ta.Any) -> T:
    return _inspect.tag(obj, **kwargs)


def build_kwargs_target(
        obj: ta.Any,
        *,
        skip_args: int = 0,
        skip_kwargs: ta.Iterable[str] | None = None,
        raw_optional: bool = False,
        non_strict: bool = False,
) -> KwargsTarget:
    return _inspect.build_kwargs_target(
        obj,
        skip_args=skip_args,
        skip_kwargs=skip_kwargs,
        raw_optional=raw_optional,
        non_strict=non_strict,
    )


##


def target(**kwargs: ta.Any) -> ta.Callable[[ta.Any], KwargsTarget]:
    def inner(obj: ta.Any) -> KwargsTarget:
        return KwargsTarget.of(obj, **kwargs)
    return inner
