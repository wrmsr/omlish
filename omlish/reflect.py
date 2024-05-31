"""
TODO:
"""
import collections.abc
import typing as ta
import types

from . import c3


_NoneType = types.NoneType  # type: ignore

_NONE_TYPE_FROZENSET: ta.FrozenSet['Type'] = frozenset([_NoneType])


_GenericAlias = ta._GenericAlias  # type: ignore  # noqa
_SpecialGenericAlias = ta._SpecialGenericAlias  # type: ignore  # noqa
_UnionGenericAlias = ta._UnionGenericAlias   # type: ignore  # noqa


##


class _Special(ta.NamedTuple):
    name: str
    alias: _SpecialGenericAlias  # type: ignore
    origin: type
    nparams: int


_KNOWN_SPECIALS = [
    _Special(
        v._name,  # noqa
        v,
        v.__origin__,
        v._nparams,  # noqa
    )
    for v in ta.__dict__.values()
    if isinstance(v, _SpecialGenericAlias)
]

_KNOWN_SPECIALS_BY_NAME = {s.name: s for s in _KNOWN_SPECIALS}
_KNOWN_SPECIALS_BY_ALIAS = {s.alias: s for s in _KNOWN_SPECIALS}
_KNOWN_SPECIALS_BY_ORIGIN = {s.origin: s for s in _KNOWN_SPECIALS}

_KNOWN_SPECIAL_TYPE_VARS = tuple(
    ta.TypeVar(f'_{i}')  # noqa
    for i in range(max(s.nparams for s in _KNOWN_SPECIALS) + 1)
)


##


try:
    from types import get_original_bases  # type: ignore
except ImportError:
    def get_original_bases(cls, /):
        try:
            return cls.__dict__.get('__orig_bases__', cls.__bases__)
        except AttributeError:
            raise TypeError(f'Expected an instance of type, not {type(cls).__name__!r}') from None


def get_params(obj: ta.Any) -> tuple[ta.TypeVar, ...]:
    if isinstance(obj, type):
        if issubclass(obj, ta.Generic):  # type: ignore
            return obj.__dict__.get('__parameters__', ())  # noqa

        if (ks := _KNOWN_SPECIALS_BY_ORIGIN.get(obj)) is not None:
            return _KNOWN_SPECIAL_TYPE_VARS[:ks.nparams]

    raise TypeError(obj)


##


Type = ta.Union[
    type,
    ta.TypeVar,
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
    cls: type
    args: tuple[Type, ...]
    params: tuple[ta.TypeVar, ...]
    obj: ta.Any

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'cls={self.cls.__name__}, '
            f'args={self.args!r}, '
            f'params={self.params!r})'
        )


TYPES: tuple[type, ...] = (
    type,
    ta.TypeVar,
    Union,
    Generic,
)


def type_(obj: ta.Any) -> Type:
    if isinstance(obj, (Union, Generic, ta.TypeVar)):
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
            origin,
            tuple(type_(a) for a in args),
            params,
            obj,
        )

    if isinstance(obj, type):
        if issubclass(obj, ta.Generic):  # type: ignore
            params = get_params(obj)
            return Generic(
                obj,
                params,
                params,
                obj,
            )
        return obj

    if isinstance(obj, _SpecialGenericAlias):
        if (ks := _KNOWN_SPECIALS_BY_ALIAS.get(obj)) is not None:
            params = _KNOWN_SPECIAL_TYPE_VARS[:ks.nparams]
            return Generic(
                ks.origin,
                params,
                params,
                obj,
            )

    raise TypeError(obj)


##


def types_equivalent(l: Type, r: Type) -> bool:
    if isinstance(l, Generic) and isinstance(r, Generic):
        return l.cls == r.cls and l.args == r.args
    return l == r


def get_concrete_type(ty: Type) -> ta.Optional[type]:
    if isinstance(ty, type):
        return ty
    if isinstance(ty, Generic):
        return ty.cls
    if isinstance(ty, (Union, ta.TypeVar)):
        return None
    raise TypeError(ty)


def get_type_var_replacements(ty: Type) -> ta.Mapping[ta.TypeVar, Type]:
    if isinstance(ty, Generic):
        return dict(zip(ty.params, ty.args))
    return {}


def replace_type_vars(ty: Type, rpl: ta.Mapping[ta.TypeVar, Type]) -> Type:
    if isinstance(ty, Generic):
        return ty._replace(args=tuple(rpl.get(a, a) if isinstance(a, ta.TypeVar) else a for a in ty.args))
    return ty


def get_reflected_bases(ty: Type) -> tuple[Type, ...]:
    if (cty := get_concrete_type(ty)) is not None:
        rpl = get_type_var_replacements(ty)
        return tuple(replace_type_vars(type_(b), rpl) for b in get_original_bases(cty))
    return ()


def generic_mro(obj: ta.Any) -> list[Type]:
    mro = c3.mro(
        type_(obj),
        get_bases=get_reflected_bases,
        is_subclass=lambda l, r: issubclass(get_concrete_type(l), get_concrete_type(r)),
    )
    return [ty for ty in mro if get_concrete_type(ty) is not ta.Generic]


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
