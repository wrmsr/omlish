"""
TODO:
"""
import collections.abc
import typing as ta
import types


_NoneType = types.NoneType  # type: ignore

_NONE_TYPE_FROZENSET: ta.FrozenSet['Type'] = frozenset([_NoneType])


_GenericAlias = ta._GenericAlias  # type: ignore  # noqa
_UnionGenericAlias = ta._UnionGenericAlias   # type: ignore  # noqa


try:
    from types import get_original_bases
except ImportError:
    def get_original_bases(cls, /):
        try:
            return cls.__dict__.get('__orig_bases__', cls.__bases__)
        except AttributeError:
            raise TypeError(f'Expected an instance of type, not {type(cls).__name__!r}') from None


def get_params(obj: ta.Any) -> tuple[ta.TypeVar, ...]:
    if isinstance(obj, type) and issubclass(obj, ta.Generic) and obj is not ta.Generic:
        return obj.__parameters__  # noqa
    raise TypeError(obj)


Type = ta.Union[
    type,
    'Union',
    'Generic',
]


class Union(ta.NamedTuple):
    args: ta.FrozenSet[Type]

    @property
    def is_optional(self) -> bool:
        return _NoneType in self.args

    def without_none(self) -> Type:
        if _NoneType not in self.args:
            return self
        rem = self.args - _NONE_TYPE_FROZENSET
        if len(rem) == 1:
            return next(iter(rem))
        return Union(rem)


class Generic(ta.NamedTuple):
    cls: ta.Any
    args: tuple[Type, ...]
    params: tuple[ta.TypeVar, ...]


TYPES: tuple[type, ...] = (
    type,
    ta.TypeVar,
    Union,
    Generic,
)


def type_(obj: ta.Any) -> Type:
    if isinstance(obj, (Union, Generic)):
        return obj

    if type(obj) is _UnionGenericAlias:
        return Union(frozenset(type_(a) for a in ta.get_args(obj)))

    if type(obj) is _GenericAlias or type(obj) is ta.GenericAlias:  # type: ignore  # noqa
        origin = ta.get_origin(obj)
        args = ta.get_args(obj)
        if origin is ta.Generic:
            params = args
        else:
            params = get_params(origin)
        if len(args) != len(params):
            raise TypeError(f'Mismatched {args=} and {params=} for {obj=}')
        return Generic(
            type_(origin),
            tuple(type_(a) for a in args),
            params,
        )

    if isinstance(obj, (type, ta.TypeVar)):
        return obj

    raise TypeError(obj)


##


KNOWN_GENERICS: ta.AbstractSet[type] = frozenset([
    collections.abc.Mapping,
    collections.abc.Sequence,
    collections.abc.Set,
])


def isinstance_of(rfl: Type) -> ta.Callable[[ta.Any], bool]:
    if isinstance(rfl, type):
        return lambda o: isinstance(o, rfl)

    if isinstance(rfl, Union):
        fns = [isinstance_of(a) for a in rfl.args]
        return lambda o: any(fn(o) for fn in fns)

    if isinstance(rfl, Generic):
        if rfl.cls in (collections.abc.Sequence, collections.abc.Set):
            [efn] = map(isinstance_of, rfl.args)
            return lambda o: isinstance(o, rfl.cls) and all(efn(e) for e in o)

        if rfl.cls == collections.abc.Mapping:
            kfn, vfn = map(isinstance_of, rfl.args)
            return lambda o: isinstance(o, rfl.cls) and all(kfn(k) and vfn(v) for k, v in o.items())

    raise TypeError(rfl)
