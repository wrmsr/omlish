"""
TODO:
 - visitor / transformer
 - uniform collection isinstance - items() for mappings, iter() for other
 - also check instance type in isinstance not just items lol
 - ta.Generic in mro causing trouble - omit? no longer 1:1
 - cache this shit, esp generic_mro shit
  - cache __hash__ in Generic/Union
"""
import dataclasses as dc
import types
import typing as ta


_NoneType = types.NoneType  # type: ignore

_NONE_TYPE_FROZENSET: frozenset['Type'] = frozenset([_NoneType])


_GenericAlias = ta._GenericAlias  # type: ignore  # noqa
_CallableGenericAlias = ta._CallableGenericAlias  # type: ignore  # noqa
_SpecialGenericAlias = ta._SpecialGenericAlias  # type: ignore  # noqa
_UnionGenericAlias = ta._UnionGenericAlias   # type: ignore  # noqa
_AnnotatedAlias = ta._AnnotatedAlias  # type: ignore  # noqa


##


@dc.dataclass(frozen=True)
class _Special:
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
    for v in ta.__dict__.values()  # noqa
    if isinstance(v, _SpecialGenericAlias)
]

_KNOWN_SPECIALS_BY_NAME = {s.name: s for s in _KNOWN_SPECIALS}
_KNOWN_SPECIALS_BY_ALIAS = {s.alias: s for s in _KNOWN_SPECIALS}
_KNOWN_SPECIALS_BY_ORIGIN = {s.origin: s for s in _KNOWN_SPECIALS}

_MAX_KNOWN_SPECIAL_TYPE_VARS = 16

_KNOWN_SPECIAL_TYPE_VARS = tuple(
    ta.TypeVar(f'_{i}')  # noqa
    for i in range(_MAX_KNOWN_SPECIAL_TYPE_VARS)
)


##


_SIMPLE_GENERIC_ALIAS_TYPES: set[type] = set()


def is_simple_generic_alias_type(oty: type) -> bool:
    return (
        oty is _GenericAlias or
        oty is ta.GenericAlias or  # type: ignore  # noqa
        oty in _SIMPLE_GENERIC_ALIAS_TYPES
    )


def get_params(obj: ta.Any) -> tuple[ta.TypeVar, ...]:
    if isinstance(obj, type):
        if issubclass(obj, ta.Generic):  # type: ignore
            return obj.__dict__.get('__parameters__', ())  # noqa

        if (ks := _KNOWN_SPECIALS_BY_ORIGIN.get(obj)) is not None:
            if (np := ks.nparams) < 0:
                raise TypeError(obj)
            return _KNOWN_SPECIAL_TYPE_VARS[:np]

    oty = type(obj)

    if is_simple_generic_alias_type(oty):
        return obj.__dict__.get('__parameters__', ())  # noqa

    if oty is _CallableGenericAlias:
        raise NotImplementedError('get_params not yet implemented for typing.Callable')

    raise TypeError(obj)


def is_union_type(cls: ta.Any) -> bool:
    if hasattr(ta, 'UnionType'):
        return ta.get_origin(cls) in {ta.Union, getattr(ta, 'UnionType')}

    else:
        return ta.get_origin(cls) in {ta.Union}


def get_orig_bases(obj: ta.Any) -> ta.Any:
    return obj.__orig_bases__  # noqa


def get_orig_class(obj: ta.Any) -> ta.Any:
    return obj.__orig_class__  # noqa


def get_newtype_supertype(obj: ta.Any) -> ta.Any:
    return obj.__supertype__


##


Type: ta.TypeAlias = ta.Union[
    type,
    ta.TypeVar,
    'Union',
    'Generic',
    'NewType',
    'Annotated',
    'Any',
]


@dc.dataclass(frozen=True)
class Union:
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


@dc.dataclass(frozen=True)
class Generic:
    cls: type
    args: tuple[Type, ...]                                                # map[int, V] = (int, V) | map[T, T] = (T, T)

    params: tuple[ta.TypeVar, ...] = dc.field(compare=False, repr=False)  # map[int, V] = (_0, _1) | map[T, T] = (_0, _1)  # noqa
    # params2: tuple[ta.TypeVar, ...]                                     # map[int, V] = (V,)     | map[T, T] = (T,)

    obj: ta.Any = dc.field(compare=False, repr=False)

    # def __post_init__(self) -> None:
    #     if not isinstance(self.cls, type):
    #         raise TypeError(self.cls)

    def full_eq(self, other: 'Generic') -> bool:
        return (
            self.cls == other.cls and
            self.args == other.args and
            self.params == other.params and
            self.obj == other.obj
        )


@dc.dataclass(frozen=True)
class NewType:
    obj: ta.Any
    ty: Type


@dc.dataclass(frozen=True)
class Annotated:
    ty: Type
    md: ta.Sequence[ta.Any]

    obj: ta.Any = dc.field(compare=False, repr=False)


class Any:
    pass


ANY = Any()


TYPES: tuple[type, ...] = (
    type,
    ta.TypeVar,
    Union,
    Generic,
    NewType,
    Annotated,
    Any,
)


##


class Reflector:
    def __init__(
            self,
            *,
            override: ta.Callable[[ta.Any], ta.Any] | None = None,
    ) -> None:
        super().__init__()

        self._override = override

    def is_type(self, obj: ta.Any) -> bool:
        if isinstance(obj, (Union, Generic, ta.TypeVar, NewType, Any)):  # noqa
            return True

        oty = type(obj)

        return (
                oty is _UnionGenericAlias or oty is types.UnionType or  # noqa

                isinstance(obj, ta.NewType) or  # noqa

                (
                    is_simple_generic_alias_type(oty) or
                    oty is _CallableGenericAlias
                ) or

                isinstance(obj, type) or

                isinstance(obj, _SpecialGenericAlias)
        )

    def type(self, obj: ta.Any) -> Type:
        if self._override is not None:
            if (ovr := self._override(obj)) is not None:
                return ovr

        if obj is ta.Any:
            return ANY

        if isinstance(obj, (Union, Generic, ta.TypeVar, NewType, Any)):  # noqa
            return obj

        oty = type(obj)

        if oty is _UnionGenericAlias or oty is types.UnionType:
            return Union(frozenset(self.type(a) for a in ta.get_args(obj)))

        if isinstance(obj, ta.NewType):  # noqa
            return NewType(obj, get_newtype_supertype(obj))

        if (
                is_simple_generic_alias_type(oty) or
                oty is _CallableGenericAlias
        ):
            origin = ta.get_origin(obj)
            args = ta.get_args(obj)

            if oty is _CallableGenericAlias:
                p, r = args
                if p is Ellipsis or isinstance(p, ta.ParamSpec):
                    raise TypeError(f'Callable argument not yet supported for {obj=}')
                args = (*p, r)
                params = _KNOWN_SPECIAL_TYPE_VARS[:len(args)]

            elif origin is tuple:
                params = _KNOWN_SPECIAL_TYPE_VARS[:len(args)]

            elif origin is ta.Generic:
                params = args

            else:
                params = get_params(origin)

            if len(args) != len(params):
                raise TypeError(f'Mismatched {args=} and {params=} for {obj=}')

            return Generic(
                origin,
                tuple(self.type(a) for a in args),
                params,
                obj,
            )

        if isinstance(obj, type):
            if issubclass(obj, ta.Generic):  # type: ignore
                params = get_params(obj)
                if params:
                    return Generic(
                        obj,
                        params,
                        params,
                        obj,
                    )
            return obj

        if isinstance(obj, _SpecialGenericAlias):
            if (ks := _KNOWN_SPECIALS_BY_ALIAS.get(obj)) is not None:
                if (np := ks.nparams) < 0:
                    raise TypeError(obj)
                params = _KNOWN_SPECIAL_TYPE_VARS[:np]
                return Generic(
                    ks.origin,
                    params,
                    params,
                    obj,
                )

        if isinstance(obj, _AnnotatedAlias):
            o = ta.get_args(obj)[0]
            return Annotated(self.type(o), md=obj.__metadata__, obj=obj)

        raise TypeError(obj)


DEFAULT_REFLECTOR = Reflector()

is_type = DEFAULT_REFLECTOR.is_type
type_ = DEFAULT_REFLECTOR.type
