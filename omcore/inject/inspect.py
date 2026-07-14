import typing as ta

from .. import check
from .. import collections as col
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


@dc.dataclass(frozen=True)
@dc.extra_class_params(cache_hash=True, terse_repr=True)
class Kwargs(ta.Sequence[Kwarg], lang.Final):
    seq: ta.Sequence[Kwarg] = dc.xfield(coerce=tuple)

    def __post_init__(self) -> None:
        if bad := {kw for kw in self.seq if not isinstance(kw, Kwarg)}:
            raise TypeError(bad)
        hash(self)

    @classmethod
    def of(
            cls,
            *kws: Kwarg,
            **kwargs: tuple[Key | ta.Any, bool] | Key | ta.Any,
    ) -> Kwargs:
        lst: list[Kwarg] = list(kws)
        for n, v in kwargs.items():
            if isinstance(v, tuple):
                kw_k, kw_hd = v
                lst.append(Kwarg(n, as_key(kw_k), has_default=kw_hd))
            else:
                lst.append(Kwarg(n, as_key(v)))
        return Kwargs(tuple(lst))

    #

    @dc.init
    @lang.cached_property
    def by_name(self) -> ta.Mapping[str, Kwarg]:
        return col.make_map(((kw.name, kw) for kw in self.seq), strict=True)

    @lang.cached_property
    def by_key(self) -> ta.Mapping[Key, ta.Sequence[Kwarg]]:
        raise NotImplementedError

    #

    @ta.overload
    def __getitem__(self, index: str | int, /) -> Kwarg: ...

    @ta.overload
    def __getitem__(self, index: Key | slice, /) -> ta.Sequence[Kwarg]: ...

    def __getitem__(self, index, /):
        if isinstance(index, str):
            return self.by_name[index]
        elif isinstance(index, Key):
            return self.by_key[index]
        else:
            return self.seq[index]

    def __len__(self) -> int:
        return len(self.seq)

    def __iter__(self) -> ta.Iterator[Kwarg]:
        return iter(self.seq)

    def __contains__(self, value: str | Key | Kwarg, /) -> bool:  # type: ignore[override]
        if isinstance(value, str):
            return value in self.by_name
        elif isinstance(value, Key):
            return value in self.by_key
        elif isinstance(value, Kwarg):
            return value in self.seq
        else:
            raise TypeError(value)

    #

    def override(
            self,
            *kws: Kwarg,
            **kwargs: tuple[Key | ta.Any, bool] | Key | ta.Any,
    ) -> Kwargs:
        if not kws and not kwargs:
            return self

        new_kws: dict[str, Kwarg] = {kw.name: kw for kw in self.seq}
        for kw in Kwargs.of(*kws, **kwargs):
            new_kws[kw.name] = kw
        return Kwargs(tuple(new_kws.values()))

    def drop(self, *what: str | Key, strict: bool = False) -> Kwargs:
        if not what:
            return self

        if strict:
            if missing := [cur for cur in what if cur not in self]:
                raise KeyError(missing)

        names: set[str] = set()
        keys: set[Key] = set()
        for cw in what:
            if isinstance(cw, str):
                names.add(cw)
            elif isinstance(cw, Key):
                keys.add(cw)
            else:
                raise TypeError(cw)

        return Kwargs(tuple(
            cur
            for cur in self.seq
            if cur.name not in names and cur.key not in keys
        ))


@dc.dataclass(frozen=True)
@dc.extra_class_params(cache_hash=True, terse_repr=True)
class KwargsTarget(lang.Final):
    obj: ta.Any
    kwargs: Kwargs

    @classmethod
    def of(
            cls,
            obj: ta.Any,
            *kws: Kwarg,
            **kwargs: tuple[Key | ta.Any, bool] | Key | ta.Any,
    ) -> KwargsTarget:
        return cls(obj, Kwargs.of(*kws, **kwargs))

    #

    def override(
            self,
            *kws: Kwarg,
            **kwargs: tuple[Key | ta.Any, bool] | Key | ta.Any,
    ) -> KwargsTarget:
        if not kws and not kwargs:
            return self
        return dc.replace(self, kwargs=self.kwargs.override(*kws, **kwargs))

    def drop(self, *what: str | Key, strict: bool = False) -> KwargsTarget:
        if not what:
            return self
        return dc.replace(self, kwargs=self.kwargs.drop(*what, strict=strict))


##


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
