"""
This is all gross, but this business always tends to be, and it at least centralizes and abstracts away all the
grossness and hides it behind a small and stable interface. It supports exactly as much as is needed by the codebase at
any given moment. It is 90% of why the codebase is strictly 3.13+ - I've tried to maintain backwards compat with this
kind of thing many times before and it's not worth my time, especially with lite code as an alternative.

I'm exploring extracting and distilling down mypy's type system to replace all of this, both to add some formalism /
give it some guiding North Star to make all of its decisions for it, and to add some long sought capabilities (infer,
meet, join, solve, ...), but it's quite a bit of work and not a priority at the moment.

TODO:
 - refactor like a GuardFn? - no check_only, return a closure to continue computation - worse? slower?
 - cache this shit
  - especially generic_mro shit
 - ultimately fold generic replacement into another Reflector dimension
 - replace reflector `isinstance`'s with `is` for internal `typing` types where possible
  - dispatch table fast path?
"""
import dataclasses as dc
import reprlib
import threading
import types
import typing as ta

from ..lite.abstract import Abstract
from ..lite.dataclasses import install_dataclass_cache_hash


_NoneType = types.NoneType  # type: ignore

_NONE_TYPE_FROZENSET: frozenset[Type] = frozenset([_NoneType])


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


@ta.final
@install_dataclass_cache_hash()
@dc.dataclass(frozen=True)
class _Special:
    name: str
    alias: _SpecialGenericAlias  # type: ignore
    origin: type
    nparams: int

    @classmethod
    def from_alias(cls, sa: _SpecialGenericAlias) -> _Special:  # type: ignore
        return cls(
            sa._name,  # type: ignore  # noqa
            sa,
            sa.__origin__,  # type: ignore
            sa._nparams,  # type: ignore  # noqa
        )


@ta.final
@install_dataclass_cache_hash()
@dc.dataclass(frozen=True)
class _LazySpecial:
    name: str


@ta.final
class _KnownSpecials:
    def __init__(
            self,
            specials: ta.Iterable[_Special] = (),
            lazy_specials: ta.Iterable[_LazySpecial] = (),
    ) -> None:
        super().__init__()

        self._lock = threading.RLock()

        self._lst: list[_Special] = []
        self._by_name: dict[str, _Special] = {}
        self._by_alias: dict[_SpecialGenericAlias, _Special] = {}  # type: ignore
        self._by_origin: dict[type, _Special] = {}

        self._lazies_by_name: dict[str, _LazySpecial] = {}

        for sp in specials:
            self._add(sp)
        for lz in lazy_specials:
            self._add_lazy(lz)

    #

    def _add(self, sp: _Special) -> None:
        uds: list[tuple[ta.Any, ta.MutableMapping]] = [
            (sp.name, self._by_name),
            (sp.alias, self._by_alias),
            (sp.origin, self._by_origin),
        ]
        for k, dct in uds:
            if k in dct:
                raise KeyError(k)

        if sp.name in self._lazies_by_name:
            raise KeyError(sp.name)

        self._lst.append(sp)
        for k, dct in uds:
            dct[k] = sp

    def add(self, *specials: _Special) -> ta.Self:
        with self._lock:
            for sp in specials:
                self._add(sp)
        return self

    #

    def _add_lazy(self, lz: _LazySpecial) -> None:
        if lz.name in self._lazies_by_name:
            raise KeyError(lz.name)
        if lz.name in self._by_name:
            raise KeyError(lz.name)

        self._lazies_by_name[lz.name] = lz

    def add_lazy(self, *lazy_specials: _LazySpecial) -> ta.Self:
        with self._lock:
            for lz in lazy_specials:
                self._add_lazy(lz)
        return self

    #

    def _get_lazy_by_name(self, name: str) -> _Special | None:
        if name not in self._lazies_by_name:
            return None

        with self._lock:
            if (x := self._by_name.get(name)) is not None:
                return x

            if (lz := self._lazies_by_name.get(name)) is None:
                return None

            sa = getattr(ta, lz.name)
            if not isinstance(sa, _SpecialGenericAlias):
                raise TypeError(sa)

            sp = _Special.from_alias(sa)
            del self._lazies_by_name[lz.name]
            self._add(sp)

            return sp

    def get_by_name(self, name: str) -> _Special | None:
        try:
            return self._by_name.get(name)
        except KeyError:
            pass
        return self._get_lazy_by_name(name)

    def get_by_alias(self, alias: _SpecialGenericAlias) -> _Special | None:  # type: ignore
        try:
            return self._by_alias[alias]
        except KeyError:
            pass
        return self._get_lazy_by_name(alias._name)  # type: ignore  # noqa

    def get_by_origin(self, origin: type) -> _Special | None:
        return self._by_origin.get(origin)


_KNOWN_SPECIALS = _KnownSpecials(
    [
        _Special.from_alias(v)
        for v in ta.__dict__.values()  # noqa
        if isinstance(v, _SpecialGenericAlias)
    ],
    [
        _LazySpecial(n)
        for n in [
            # https://github.com/python/cpython/commit/e8be0c9c5a7c2327b3dd64009f45ee0682322dcb
            'Pattern',
            'Match',
            'ContextManager',
            'AsyncContextManager',
            # https://github.com/python/cpython/commit/305be5fb1a1ece7f9651ae98053dbe79bf439aa4
            'ForwardRef',
        ]
        if n not in ta.__dict__
    ],
)


##


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
        if issubclass(obj, ta.Generic):
            return obj.__dict__.get('__parameters__', ())  # noqa

        if (ks := _KNOWN_SPECIALS.get_by_origin(obj)) is not None:
            if (np := ks.nparams) < 0:
                raise TypeError(obj)
            return _KNOWN_SPECIAL_TYPE_VARS[:np]

    oty = type(obj)

    if is_simple_generic_alias_type(oty):
        return obj.__dict__.get('__parameters__', ())  # noqa

    if isinstance(obj, ta.TypeAliasType):
        return obj.__parameters__

    if oty is _CallableGenericAlias:
        raise NotImplementedError('get_params not yet implemented for typing.Callable')

    raise TypeError(obj)


def _is_immediate_protocol(obj: ta.Any) -> bool:
    return isinstance(obj, _ProtocolMeta) and obj.__dict__['_is_protocol']


def is_union_type(cls: ta.Any) -> bool:
    if hasattr(ta, 'UnionType'):
        return ta.get_origin(cls) in {ta.Union, getattr(ta, 'UnionType')}

    else:
        return ta.get_origin(cls) == ta.Union


def is_annotated_type(obj: ta.Any) -> bool:
    return isinstance(obj, _AnnotatedAlias)


def get_annotated_type_metadata(obj: ta.Any) -> ta.Sequence[ta.Any]:
    if not is_annotated_type(obj):
        raise TypeError(obj)
    return obj.__metadata__


def get_orig_bases(obj: ta.Any) -> ta.Any:
    return obj.__orig_bases__  # noqa


def get_orig_class(obj: ta.Any) -> ta.Any:
    return obj.__orig_class__  # noqa


def get_newtype_supertype(obj: ta.Any) -> ta.Any:
    return obj.__supertype__


def get_type_var_bound(obj: ta.Any) -> ta.Any:
    return obj.__bound__


##


class TypeInfo(Abstract):
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


class _LateUnionArgs(list):
    pass


@ta.final
class Union(TypeInfo):
    def __init__(self, args: frozenset[Type] | _LateUnionArgs) -> None:
        if isinstance(args, _LateUnionArgs):
            self._late_args = args
        else:
            self._args = args

    @property
    def args(self) -> frozenset[Type]:
        try:
            return self._args
        except AttributeError:
            pass
        args = self._args = frozenset(self._late_args)
        return args

    @reprlib.recursive_repr()
    def __repr__(self) -> str:
        try:
            args = self._args
        except AttributeError:
            return f'{self.__class__.__name__}({self._late_args!r})'
        return f'{self.__class__.__name__}({args!r})'

    _hash: int

    def __hash__(self) -> int:
        try:
            return self._hash
        except AttributeError:
            h = self._hash = hash(self.args)
            return h

    def __eq__(self, other):
        if other is self:
            return True
        if not isinstance(other, Union):
            return NotImplemented
        return self.args == other.args

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
class GenericLike(TypeInfo, Abstract, ta.Generic[GenericLikeCls]):
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
        if not (isinstance(self.args, tuple) and isinstance(self.params, tuple) and len(self.args) == len(self.params)):
            raise ReflectTypeError(f'GenericLike {self.args=} and {self.params=} must be equal length tuples')

    def full_eq(self, other: GenericLike) -> bool:
        return (
            type(self) is type(other) and
            self.cls == other.cls and
            self.args == other.args and
            self.params == other.params and
            self.obj == other.obj
        )


@ta.final
@install_dataclass_cache_hash()
@dc.dataclass(frozen=True)
class Generic(GenericLike[type]):
    pass


@ta.final
@install_dataclass_cache_hash()
@dc.dataclass(frozen=True)
class Protocol(GenericLike[ta.Any]):
    # cls will still be a type - it will be the topmost _is_protocol=True class.
    # it may however be ta.Protocol, which *is* a `type` at runtime, but not according to mypy.
    pass


@ta.final
@install_dataclass_cache_hash()
@dc.dataclass(frozen=True)
class TypeAlias(GenericLike[ta.Any]):
    pass


#


@ta.final
@install_dataclass_cache_hash()
@dc.dataclass(frozen=True)
class NewType(TypeInfo):
    obj: ta.Any
    ty: Type


#


@ta.final
@install_dataclass_cache_hash()
@dc.dataclass(frozen=True)
class Annotated(TypeInfo):
    ty: Type
    md: tuple[ta.Any, ...]

    obj: ta.Any = dc.field(compare=False, repr=False)

    def __post_init__(self) -> None:
        if not (isinstance(self.md, tuple) and self.md):
            raise TypeError(f'Annotated {self.md=} must non-empty tuple')
        if isinstance(self.ty, Annotated):
            raise TypeError(self.ty)


#


@ta.final
@install_dataclass_cache_hash()
@dc.dataclass(frozen=True)
class Literal(TypeInfo):
    args: tuple[ta.Any, ...]

    obj: ta.Any = dc.field(compare=False, repr=False)

    def __post_init__(self) -> None:
        if not (isinstance(self.args, tuple) and self.args):
            raise TypeError(f'Literal {self.args=} must non-empty tuple')


#


@ta.final
@install_dataclass_cache_hash()
@dc.dataclass(frozen=True)
class ForwardRef(TypeInfo):
    # Note that this isn't `obj` like the others - this is fundamentally required for its handling and cannot be
    # stripped.
    ref: ta.ForwardRef

    def __post_init__(self) -> None:
        if not isinstance(self.ref, ta.ForwardRef):
            raise TypeError(self.ref)


#


@ta.final
class Recursive(TypeInfo):
    _ty: Type

    @property
    def ty(self) -> Type:
        return self._ty

    @reprlib.recursive_repr()
    def __repr__(self) -> str:
        try:
            ty = self._ty
        except AttributeError:
            return f'{type(self).__name__}@{id(self):x}!UNBOUND'
        return f'{type(self).__name__}({ty!r})'

    def __hash__(self) -> int:
        return hash(self._ty)

    def __eq__(self, other: object) -> bool:
        if self is other:
            return True
        if not isinstance(other, Recursive):
            return self._ty == other
        return self._ty == other._ty


#


class Any(TypeInfo):
    pass


ANY = Any()


##


class ReflectTypeError(TypeError):
    pass


class RecursiveTypeError(TypeError):
    pass


_TRIVIAL_TYPES: set[ta.Any] = {
    bool,
    int,
    str,
    float,
    object,
    type(None),
}


# TODO: speed up is_type: `if obj.__class__ in _NOT_SUBCLASSED_SPECIAL_TYPES: return True`
# _NOT_SUBCLASSED_SPECIAL_TYPES: set[type] = {
#     type(ta.Any),
#     _UnionGenericAlias,
#     ta.NewType,
# }
# TODO: static_init(for t in _NOT_SUBCLASSED_SPECIAL_TYPES: if (sts := t.__subclasses__()): raise TypeError)


class Reflector:
    def __init__(
            self,
            *,
            override: ta.Callable[[ta.Any], ta.Any] | None = None,
            preserve_type_aliases: bool = False,
            allow_recursion: bool = False,
    ) -> None:
        super().__init__()

        self._override = override
        self._preserve_type_aliases = preserve_type_aliases
        self._allow_recursion = allow_recursion

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

    @ta.overload
    def _type(
            self,
            obj: ta.Any,
            *,
            check_only: ta.Literal[True],
    ) -> None:
        ...

    @ta.overload
    def _type(
            self,
            obj: ta.Any,
            *,
            check_only: ta.Literal[False] = False,
    ) -> Type:
        ...

    def _type(
            self,
            obj,
            *,
            check_only=False,
    ):
        if not check_only:
            aliases: dict = {}
            cur_aliases: set = set()

        def rec(cur: ta.Any) -> ta.Any:
            ##
            # Overrides beat everything

            if self._override is not None:
                if (ovr := self._override(cur)) is not None:
                    return ovr

            ##
            # Any

            if cur is ta.Any:
                return ANY

            ##
            # Trivial

            try:
                if cur in _TRIVIAL_TYPES:
                    return cur
            except TypeError:
                pass

            ##
            # Already a Type?

            if isinstance(cur, (ta.TypeVar, TypeInfo)):  # noqa
                return cur

            ##
            # It's a type

            oty = type(cur)

            ##
            # Union

            if oty is _UnionGenericAlias or oty is types.UnionType:
                if check_only:
                    return None

                return Union(
                    (_LateUnionArgs if self._allow_recursion and aliases else frozenset)
                    ([rec(a) for a in ta.get_args(cur)]),
                )

            ##
            # NewType

            if isinstance(cur, ta.NewType):  # noqa
                if check_only:
                    return None

                return NewType(cur, get_newtype_supertype(cur))

            ##
            # Simple Generic

            if (
                    is_simple_generic_alias_type(oty) or
                    oty is _CallableGenericAlias
            ):
                if check_only:
                    return None

                origin = ta.get_origin(cur)

                args = ta.get_args(cur)

                if origin is ta.Protocol:
                    params = get_params(cur)

                elif oty is _CallableGenericAlias:
                    p, r = args
                    if p is Ellipsis or isinstance(p, ta.ParamSpec):
                        raise ReflectTypeError(f'Callable argument not yet supported for {cur=}')
                    args = (*p, r)
                    params = _KNOWN_SPECIAL_TYPE_VARS[:len(args)]

                elif origin is tuple:
                    params = _KNOWN_SPECIAL_TYPE_VARS[:len(args)]

                elif origin is ta.Generic:
                    params = args

                else:
                    params = get_params(origin)

                if len(args) != len(params):
                    raise ReflectTypeError(f'Mismatched {args=} and {params=} for {cur=}')

                if not isinstance(origin, type):
                    raise ReflectTypeError(f'Generic origin {origin!r} is not a type')

                if origin is ta.Protocol:
                    if args != params:  # type: ignore[unreachable]
                        raise ReflectTypeError(f'Protocol argument not yet supported for {args=}, {params=}')
                    return Protocol(
                        ta.Protocol,
                        args,
                        params,
                        cur,
                    )

                r_args = tuple(rec(a) for a in args)

                if _is_immediate_protocol(origin):
                    return Protocol(
                        origin,
                        r_args,
                        params,
                        cur,
                    )

                return Generic(
                    origin,
                    r_args,
                    params,
                    cur,
                )

            ##
            # Full Generic

            if isinstance(cur, type):
                if check_only:
                    return None

                if _is_immediate_protocol(cur):
                    params = get_params(cur)
                    return Protocol(
                        cur,
                        params,
                        params,
                        cur,
                    )

                if issubclass(cur, ta.Generic):
                    params = get_params(cur)
                    if params:
                        return Generic(
                            cur,
                            params,
                            params,
                            cur,
                        )

                return cur

            ##
            # Special Generic

            if isinstance(cur, _SpecialGenericAlias):
                if (ks := _KNOWN_SPECIALS.get_by_alias(cur)) is not None:
                    if check_only:
                        return None

                    if (np := ks.nparams) < 0:
                        raise ReflectTypeError(cur)

                    params = _KNOWN_SPECIAL_TYPE_VARS[:np]
                    return Generic(
                        ks.origin,
                        params,
                        params,
                        cur,
                    )

            ##
            # Annotated

            if isinstance(cur, _AnnotatedAlias):
                if check_only:
                    return None

                o = ta.get_args(cur)[0]
                return Annotated(rec(o), md=tuple(cur.__metadata__), obj=cur)

            ##
            # Literal

            if isinstance(cur, _LiteralGenericAlias):
                if check_only:
                    return None

                return Literal(ta.get_args(cur), obj=cur)

            ##
            # ForwardRef

            if isinstance(cur, ta.ForwardRef):
                if check_only:
                    return None

                return ForwardRef(cur)

            ##
            # TypeAlias

            if isinstance(cur, ta.TypeAliasType):
                if check_only:
                    return None

                if get_params(cur):
                    raise NotImplementedError

                if cur in cur_aliases:
                    if not self._allow_recursion:
                        raise RecursiveTypeError(cur)

                    if (rc := aliases[cur]) is None:
                        rc = aliases[cur] = Recursive()

                    return rc

                # We don't have to bother with finally, any exception aborts everything anyway
                aliases[cur] = None

                cur_aliases.add(cur)
                tav = rec(cur.__value__)
                cur_aliases.remove(cur)

                if self._preserve_type_aliases:
                    tav = TypeAlias(
                        tav,
                        (),
                        (),
                        cur,
                    )

                if (rc := aliases[cur]) is not None:
                    rc._ty = tav  # noqa
                aliases[cur] = tav

                return tav

            ##
            # Failure

            raise ReflectTypeError(cur)

        return rec(obj)


DEFAULT_REFLECTOR = Reflector()

is_type = DEFAULT_REFLECTOR.is_type
type_ = DEFAULT_REFLECTOR.type
