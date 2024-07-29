"""
TODO:
 - callables..
 - uniform collection isinstance - items() for mappings, iter() for other
 - also check instance type in isinstance not just items lol
 - ta.Generic in mro causing trouble - omit? no longer 1:1
 - cache this shit, esp generic_mro shit
  - cache __hash__ in Generic/Union
"""
import collections.abc
import types
import typing as ta

from . import c3
from . import lang


if ta.TYPE_CHECKING:
    from .collections import cache
else:
    cache = lang.proxy_import('.collections.cache', __package__)


_NoneType = types.NoneType  # type: ignore

_NONE_TYPE_FROZENSET: frozenset['Type'] = frozenset([_NoneType])


_GenericAlias = ta._GenericAlias  # type: ignore  # noqa
# _CallableGenericAlias = ta._CallableGenericAlias  # type: ignore  # noqa
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


def get_params(obj: ta.Any) -> tuple[ta.TypeVar, ...]:
    if isinstance(obj, type):
        if issubclass(obj, ta.Generic):  # type: ignore
            return obj.__dict__.get('__parameters__', ())  # noqa

        if (ks := _KNOWN_SPECIALS_BY_ORIGIN.get(obj)) is not None:
            return _KNOWN_SPECIAL_TYPE_VARS[:ks.nparams]

    oty = type(obj)

    if oty is _GenericAlias or oty is ta.GenericAlias:  # type: ignore  # noqa
        return obj.__dict__.get('__parameters__', ())  # noqa

    raise TypeError(obj)


def is_union_type(cls: ta.Any) -> bool:
    if hasattr(ta, 'UnionType'):
        return ta.get_origin(cls) in {ta.Union, getattr(ta, 'UnionType')}
    else:
        return ta.get_origin(cls) in {ta.Union}


##


Type = ta.Union[
    type,
    ta.TypeVar,
    'NewType',
    'Union',
    'Generic',
]


class Union(ta.NamedTuple):
    args: frozenset[Type]

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
    args: tuple[Type, ...]             # map[int, V] = (int, V) | map[T, T] = (T, T)
    params: tuple[ta.TypeVar, ...]     # map[int, V] = (_0, _1) | map[T, T] = (_0, _1)
    # params2: tuple[ta.TypeVar, ...]  # map[int, V] = (V,)     | map[T, T] = (T,)
    obj: ta.Any

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'cls={self.cls.__name__}, '
            f'args={self.args!r}, '
            f'params={self.params!r})'
        )


class NewType(ta.NamedTuple):
    obj: ta.Any


TYPES: tuple[type, ...] = (
    type,
    ta.TypeVar,
    Union,
    Generic,
    NewType,
)


def type_(obj: ta.Any) -> Type:
    if isinstance(obj, (Union, Generic, ta.TypeVar, NewType)):  # noqa
        return obj

    oty = type(obj)

    if oty is _UnionGenericAlias or oty is types.UnionType:
        return Union(frozenset(type_(a) for a in ta.get_args(obj)))

    if isinstance(obj, ta.NewType):  # noqa
        return NewType(oty)

    if (
            oty is _GenericAlias or
            oty is ta.GenericAlias  # type: ignore  # noqa
    ):
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


def get_underlying(nt: NewType) -> Type:
    return type_(nt.obj.__supertype__)  # noqa


def get_concrete_type(ty: Type) -> type | None:
    if isinstance(ty, type):
        return ty
    if isinstance(ty, Generic):
        return ty.cls
    if isinstance(ty, NewType):
        return get_concrete_type(get_underlying(ty))
    if isinstance(ty, (Union, ta.TypeVar)):
        return None
    raise TypeError(ty)


def get_type_var_replacements(ty: Type) -> ta.Mapping[ta.TypeVar, Type]:
    if isinstance(ty, Generic):
        return dict(zip(ty.params, ty.args))
    return {}


def to_annotation(ty: Type) -> ta.Any:
    if isinstance(ty, Generic):
        return ty.obj if ty.obj is not None else ty.cls
    if isinstance(ty, Union):
        return ta.Union[*tuple(to_annotation(e) for e in ty.args)]
    if isinstance(ty, (type, ta.TypeVar, NewType)):
        return ty
    raise TypeError(ty)


def replace_type_vars(
        ty: Type,
        rpl: ta.Mapping[ta.TypeVar, Type],
        *,
        update_aliases: bool = False,
) -> Type:
    def rec(cur):
        if isinstance(cur, type):
            return cur
        if isinstance(cur, NewType):
            return cur
        if isinstance(cur, Generic):
            args = tuple(rec(a) for a in cur.args)
            if update_aliases:
                obj = cur.obj
                if (ops := get_params(obj)):
                    nargs = [to_annotation(rpl[p]) for p in ops]
                    if ta.get_origin(obj) is ta.Generic:
                        # FIXME: None? filter_typing_generic in get_generic_bases?
                        pass
                    else:
                        obj = cur.obj[*nargs]
            else:
                obj = None
            return cur._replace(args=args, obj=obj)
        if isinstance(cur, Union):
            return Union(frozenset(rec(e) for e in cur.args))
        if isinstance(cur, ta.TypeVar):
            return rpl[cur]
        raise TypeError(cur)

    return rec(ty)


class GenericSubstitution:
    def __init__(
            self,
            *,
            update_aliases: bool = False,
            cache_size: int = 0,  # FIXME: ta.Generic isn't weakrefable..
    ) -> None:
        super().__init__()

        self._update_aliases = update_aliases

        if cache_size > 0:
            self.get_generic_bases = cache.cache(weak_keys=True, max_size=cache_size)(self.get_generic_bases)  # type: ignore  # noqa
            self.generic_mro = cache.cache(weak_keys=True, max_size=cache_size)(self.generic_mro)  # type: ignore

    def get_generic_bases(self, ty: Type) -> tuple[Type, ...]:
        if (cty := get_concrete_type(ty)) is not None:
            rpl = get_type_var_replacements(ty)
            ret: list[Type] = []
            for b in types.get_original_bases(cty):
                bty = type_(b)
                if isinstance(bty, Generic) and isinstance(b, type):
                    # FIXME: throws away relative types, but can't use original vars as they're class-contextual
                    bty = type_(b[*((ta.Any,) * len(bty.params))])  # type: ignore
                rty = replace_type_vars(bty, rpl, update_aliases=self._update_aliases)
                ret.append(rty)
            return tuple(ret)
        return ()

    def generic_mro(self, obj: ta.Any) -> list[Type]:
        mro = c3.mro(
            type_(obj),
            get_bases=lambda t: self.get_generic_bases(t),
            is_subclass=lambda l, r: issubclass(get_concrete_type(l), get_concrete_type(r)),  # type: ignore
        )
        return [ty for ty in mro if get_concrete_type(ty) is not ta.Generic]


DEFAULT_GENERIC_SUBSTITUTION = GenericSubstitution()

get_generic_bases = DEFAULT_GENERIC_SUBSTITUTION.get_generic_bases
generic_mro = DEFAULT_GENERIC_SUBSTITUTION.generic_mro

ALIAS_UPDATING_GENERIC_SUBSTITUTION = GenericSubstitution(update_aliases=True)


##


KNOWN_GENERICS: ta.AbstractSet[type] = frozenset([
    collections.abc.Mapping,
    collections.abc.Sequence,
    collections.abc.Set,
])


def isinstance_of(rfl: Type) -> ta.Callable[[ta.Any], bool]:
    if isinstance(rfl, type):
        return lambda o: isinstance(o, rfl)

    if isinstance(rfl, NewType):
        return isinstance_of(get_underlying(rfl))

    if isinstance(rfl, Union):
        fns = [isinstance_of(a) for a in rfl.args]
        return lambda o: any(fn(o) for fn in fns)

    if isinstance(rfl, Generic):
        if rfl.cls in (collections.abc.Sequence, collections.abc.Set):
            [efn] = map(isinstance_of, rfl.args)
            return lambda o: isinstance(o, rfl.cls) and all(efn(e) for e in o)  # type: ignore

        if rfl.cls == collections.abc.Mapping:
            kfn, vfn = map(isinstance_of, rfl.args)
            return lambda o: isinstance(o, rfl.cls) and all(kfn(k) and vfn(v) for k, v in o.items())  # type: ignore

    raise TypeError(rfl)
