"""
TODO:
 - visitor / transformer
 - uniform collection isinstance - items() for mappings, iter() for other
 - also check instance type in isinstance not just items lol
TODO:
 - ta.Generic in mro causing trouble - omit? no longer 1:1
 - cache this shit, esp generic_mro shit
  - cache __hash__ in Generic/Union
"""
import abc
import dataclasses as dc
import types
import typing as ta


_NoneType = types.NoneType  # type: ignore

_NONE_TYPE_FROZENSET: frozenset['Type'] = frozenset([_NoneType])


_AnnotatedAlias = ta._AnnotatedAlias  # type: ignore  # noqa
_CallableGenericAlias = ta._CallableGenericAlias  # type: ignore  # noqa
_GenericAlias = ta._GenericAlias  # type: ignore  # noqa
_LiteralGenericAlias = ta._LiteralGenericAlias  # type: ignore  # noqa
_ProtocolMeta = ta._ProtocolMeta  # noqa
_SpecialGenericAlias = ta._SpecialGenericAlias  # type: ignore  # noqa
_UnionGenericAlias = ta._UnionGenericAlias   # type: ignore  # noqa


##


_Protocol = getattr(ta, 'Protocol')
_Generic = getattr(ta, 'Generic')

if not isinstance(_Protocol, type) or not issubclass(_Protocol, _Generic):
    raise TypeError(f'typing.Protocol is not a proper typing.Generic subtype')


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


def _is_immediate_protocol(obj: ta.Any) -> bool:
    return isinstance(obj, _ProtocolMeta) and obj.__dict__['_is_protocol']


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


def get_type_var_bound(obj: ta.Any) -> ta.Any:
    return obj.__bound__


##


class TypeInfo(abc.ABC):  # noqa
    pass


Type: ta.TypeAlias = ta.Union[  # noqa
    type,
    ta.TypeVar,
    TypeInfo,
]


TYPES: tuple[type, ...] = (
    type,
    ta.TypeVar,
    TypeInfo,
)


##


@dc.dataclass(frozen=True)
class Union(TypeInfo):
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


#


GenericLikeCls = ta.TypeVar('GenericLikeCls')


@dc.dataclass(frozen=True)
class GenericLike(TypeInfo, abc.ABC, ta.Generic[GenericLikeCls]):
    cls: GenericLikeCls

    # args and params are the same length - params maps to the generic origin's params:
    # args   : map[int, V] = (int, V) | map[T, T] = (T, T)
    # params : map[int, V] = (_0, _1) | map[T, T] = (_0, _1)
    args: tuple[Type, ...]
    params: tuple[ta.TypeVar, ...] = dc.field(compare=False, repr=False)

    obj: ta.Any = dc.field(compare=False, repr=False)

    def __post_init__(self) -> None:
        if not isinstance(self.cls, type):
            raise ReflectTypeError(f'GenericLike {self.cls=} must be a type')
        if len(self.args) != len(self.params):
            raise ReflectTypeError(f'GenericLike {self.args=} must be same length as {self.params=}')

    def full_eq(self, other: 'GenericLike') -> bool:
        return (
            type(self) is type(other) and
            self.cls == other.cls and
            self.args == other.args and
            self.params == other.params and
            self.obj == other.obj
        )


@dc.dataclass(frozen=True)
class Generic(GenericLike[type]):
    pass


@dc.dataclass(frozen=True)
class Protocol(GenericLike[ta.Any]):
    # cls will still be a type - it will be the topmost _is_protocol=True class.
    # it may however be ta.Protocol, which *is* a type, but not according to mypy.
    pass


#


@dc.dataclass(frozen=True)
class NewType(TypeInfo):
    obj: ta.Any
    ty: Type


#


@dc.dataclass(frozen=True)
class Annotated(TypeInfo):
    ty: Type
    md: ta.Sequence[ta.Any]

    obj: ta.Any = dc.field(compare=False, repr=False)


#


@dc.dataclass(frozen=True)
class Literal(TypeInfo):
    args: tuple[ta.Any, ...]

    obj: ta.Any = dc.field(compare=False, repr=False)


#


class Any(TypeInfo):
    pass


ANY = Any()


##


class ReflectTypeError(TypeError):
    pass


class Reflector:
    def __init__(
            self,
            *,
            override: ta.Callable[[ta.Any], ta.Any] | None = None,
    ) -> None:
        super().__init__()

        self._override = override

    #

    def is_type(self, obj: ta.Any) -> bool:
        try:
            self._type(obj, check_only=True)
        except ReflectTypeError:
            return False
        else:
            return True

    def type(self, obj: ta.Any) -> Type:
        if (ty := self._type(obj, check_only=False)) is None:
            raise RuntimeError(obj)
        return ty

    #

    def _type(self, obj: ta.Any, *, check_only: bool) -> Type | None:
        ##
        # Overrides beat everything

        if self._override is not None:
            if (ovr := self._override(obj)) is not None:
                return ovr

        ##
        # Any

        if obj is ta.Any:
            return ANY

        ##
        # Already a Type?

        if isinstance(obj, (ta.TypeVar, TypeInfo)):  # noqa
            return obj

        oty = type(obj)

        ##
        # Union

        if oty is _UnionGenericAlias or oty is types.UnionType:
            if check_only:
                return None

            return Union(frozenset(self.type(a) for a in ta.get_args(obj)))

        ##
        # NewType

        if isinstance(obj, ta.NewType):  # noqa
            if check_only:
                return None

            return NewType(obj, get_newtype_supertype(obj))

        ##
        # Simple Generic

        if (
                is_simple_generic_alias_type(oty) or
                oty is _CallableGenericAlias
        ):
            if check_only:
                return None

            origin = ta.get_origin(obj)

            args = ta.get_args(obj)

            if origin is ta.Protocol:
                params = get_params(obj)

            elif oty is _CallableGenericAlias:
                p, r = args
                if p is Ellipsis or isinstance(p, ta.ParamSpec):
                    raise ReflectTypeError(f'Callable argument not yet supported for {obj=}')
                args = (*p, r)
                params = _KNOWN_SPECIAL_TYPE_VARS[:len(args)]

            elif origin is tuple:
                params = _KNOWN_SPECIAL_TYPE_VARS[:len(args)]

            elif origin is ta.Generic:
                params = args

            else:
                params = get_params(origin)

            if len(args) != len(params):
                raise ReflectTypeError(f'Mismatched {args=} and {params=} for {obj=}')

            if not isinstance(origin, type):
                raise ReflectTypeError(f'Generic origin {origin!r} is not a type')

            if origin is ta.Protocol:
                if args != params:
                    raise ReflectTypeError(f'Protocol argument not yet supported for {args=}, {params=}')
                return Protocol(
                    ta.Protocol,
                    args,
                    params,
                    obj,
                )

            r_args = tuple(self.type(a) for a in args)

            if _is_immediate_protocol(origin):
                return Protocol(
                    origin,
                    r_args,
                    params,
                    obj,
                )

            return Generic(
                origin,
                r_args,
                params,
                obj,
            )

        ##
        # Full Generic

        if isinstance(obj, type):
            if check_only:
                return None

            if _is_immediate_protocol(obj):
                params = get_params(obj)
                return Protocol(
                    obj,
                    params,
                    params,
                    obj,
                )

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

        ##
        # Special Generic

        if isinstance(obj, _SpecialGenericAlias):
            if (ks := _KNOWN_SPECIALS_BY_ALIAS.get(obj)) is not None:
                if check_only:
                    return None

                if (np := ks.nparams) < 0:
                    raise ReflectTypeError(obj)

                params = _KNOWN_SPECIAL_TYPE_VARS[:np]
                return Generic(
                    ks.origin,
                    params,
                    params,
                    obj,
                )

        ##
        # Annotated

        if isinstance(obj, _AnnotatedAlias):
            if check_only:
                return None

            o = ta.get_args(obj)[0]
            return Annotated(self.type(o), md=obj.__metadata__, obj=obj)

        ##
        # Literal

        if isinstance(obj, _LiteralGenericAlias):
            if check_only:
                return None

            return Literal(ta.get_args(obj), obj=obj)

        ##
        # Failure

        raise ReflectTypeError(obj)


DEFAULT_REFLECTOR = Reflector()

is_type = DEFAULT_REFLECTOR.is_type
type_ = DEFAULT_REFLECTOR.type
