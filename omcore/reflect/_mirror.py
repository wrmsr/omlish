# ruff: noqa: SLF001
import annotationlib
import collections.abc as cabc
import enum
import sys
import threading
import types as pytypes
import typing as ta

from .core.substitute import substitute_type
from .core.symbols import ArgKind
from .core.symbols import TypeAlias
from .core.symbols import TypeInfo
from .core.symbols import VarianceKind
from .core.typeops import make_union
from .core.types import _ANY_TYPES
from .core.types import _NONE_TYPE
from .core.types import _UNINHABITED_TYPE
from .core.types import AnnotatedType
from .core.types import AnyType
from .core.types import CallableType
from .core.types import Instance
from .core.types import LiteralType
from .core.types import LiteralValue
from .core.types import ParamSpecType
from .core.types import ReadOnlyType
from .core.types import RequiredType
from .core.types import TupleType
from .core.types import Type
from .core.types import TypeAliasType
from .core.types import TypedDictType
from .core.types import TypeGuardedType
from .core.types import TypeOfAny
from .core.types import TypeType
from .core.types import TypeVarId
from .core.types import TypeVarLikeType
from .core.types import TypeVarTupleType
from .core.types import TypeVarType
from .core.types import UnboundType
from .core.types import UnpackType
from .core.types import is_literal_value
from .core.typevisitor import BoolTypeQuery
from .core.typevisitor import BoolTypeQueryMode
from .errors import FrozenMirrorReflectionError
from .errors import ReflectionValueError
from .errors import UnreflectableTypeError
from .known import _KNOWN_FULLNAMES_BY_TYPE
from .known import _KNOWN_TYPES_BY_FULLNAME
from .known import _KNOWNS
from .known import _KNOWNS_BY_FULLNAME
from .known import _KnownBaseArg
from .mirror import DEFAULT_UNRESOLVED_FORWARD_REF_POLICY
from .mirror import ForwardRefResolution
from .mirror import ForwardRefResolver
from .mirror import Mirror
from .mirror import TypeReflectSubstitutor
from .mirror import UnresolvedForwardRefPolicy


##


class _HasTypedDictItemWrapper(BoolTypeQuery):
    def __init__(self) -> None:
        super().__init__(BoolTypeQueryMode.ANY)

    def visit_required_type(self, typ: RequiredType) -> bool:
        return True

    def visit_read_only_type(self, typ: ReadOnlyType) -> bool:
        return True


class _ContainsAnyTypeAlias(BoolTypeQuery):
    def __init__(self, aliases: set[TypeAlias], seen: set[TypeAlias]) -> None:
        super().__init__(BoolTypeQueryMode.ANY)

        self.aliases = aliases
        self.seen = seen

    def visit_type_alias_type(self, typ: TypeAliasType) -> bool:
        if typ._alias is None:
            return self.query_types(typ._args)

        if typ._alias in self.aliases:
            return True

        if typ._alias in self.seen:
            return False

        self.seen.add(typ._alias)
        return self.query_types([*typ._args, typ._alias._target])


def _make_any() -> AnyType:
    return _ANY_TYPES[TypeOfAny.FROM_OMITTED_GENERICS]


def _is_none_type(obj: object) -> bool:
    return obj is None or obj is type(None)


def _is_literal_value(obj: object) -> bool:
    return is_literal_value(obj)


def _is_newtype(obj: object) -> bool:
    return isinstance(obj, ta.NewType)


def _is_forward_ref(obj: object) -> bool:
    return isinstance(obj, (str, annotationlib.ForwardRef))


def _is_typed_dict_class(obj: object) -> bool:
    return (
        isinstance(obj, type) and
        hasattr(obj, '__required_keys__') and
        hasattr(obj, '__optional_keys__') and
        hasattr(obj, '__annotations__')
    )


def _contains_any_type_alias(
        typ: Type,
        aliases: set[TypeAlias],
        seen: set[TypeAlias],
) -> bool:
    return typ.accept(_ContainsAnyTypeAlias(aliases, seen))


def _get_runtime_bases(origin: type) -> tuple[object, ...]:
    orig_bases = getattr(origin, '__orig_bases__', None)
    if orig_bases is not None:
        return tuple(
            base
            for base in orig_bases
            if base is not ta.NamedTuple
            and ta.get_origin(base) not in (ta.Generic, ta.Protocol)
        )

    bases = getattr(origin, '__bases__', ())
    return tuple(
        base
        for base in bases
        if base is not object
    )


##


@ta.final
class _RuntimeNamespace:
    def __init__(self) -> None:
        self.__name = f'runtime:{id(self):x}'

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}'

    @property
    def name(self) -> str:
        return self.__name


@ta.final
class _MirrorState:
    def __init__(
            self,
            *,
            parent: _MirrorState | None = None,
    ) -> None:
        super().__init__()

        # A frozen parent is immutable, so chain reads through it need no locking of any kind. An unfrozen parent would
        # require cross-mirror lock acquisition - forbidden outright.
        if parent is not None and not parent.is_frozen:
            raise ReflectionValueError('Mirror parent must be frozen')

        self.__parent = parent

        #

        self.__is_frozen: bool = False

        #

        self.__fullnames_by_type: dict[object, str] = {}
        self.__types_by_fullname: dict[str, object] = {}
        self.__infos_by_fullname: dict[str, TypeInfo] = {}

        self.__type_cache: dict[object, Type] = {}
        self.__cached_types: set[Type] = set()

        # This is 'two-step' (create TypeInfo -> 'prepare' TypeInfo) to support recursive types.
        self.__prepared_infos: set[type] = set()

        self.__runtime_aliases: dict[ta.TypeAliasType, TypeAlias] = {}

        # Aliases whose symbols have been created but whose targets have not (yet) been successfully resolved - a failed
        # resolution leaves the alias here so a later reflection retries (and heals) it.
        self.__unresolved_aliases: set[ta.TypeAliasType] = set()

        self.__type_var_namespace = _RuntimeNamespace()
        if parent is not None:
            self.__next_type_var_id: int = parent.__next_type_var_id + 1
        else:
            self.__next_type_var_id = 1

        self.__relevant_namespaces = {self.__type_var_namespace}

        #

        # A parentless mirror is self-sufficient and seeds the knowns itself; a child finds them through its chain.
        if parent is None:
            self.__fullnames_by_type.update(_KNOWN_FULLNAMES_BY_TYPE)
            self.__types_by_fullname.update(_KNOWN_TYPES_BY_FULLNAME)

    ##
    # freezing

    @property
    def is_frozen(self) -> bool:
        return self.__is_frozen

    def check_not_frozen(self) -> None:
        if self.__is_frozen:
            raise FrozenMirrorReflectionError

    def freeze(self, reflector: _TypeReflector) -> None:
        if self.__is_frozen:
            raise FrozenMirrorReflectionError

        # Heal any aliases left unresolved by failed reflection runs - a frozen symbol must never need mutation, so
        # anything unhealable fails the freeze.
        for alias_obj in list(self.__unresolved_aliases):
            reflector._get_type_alias_symbol(alias_obj)  # noqa

        if self.__unresolved_aliases:
            raise ReflectionValueError(f'Failed to resolve all type aliases: {self.__unresolved_aliases!r}')

        # Materialize and prepare every runtime class interned in this layer (including seeded knowns) so no reflection
        # through a child ever needs to mutate a frozen TypeInfo. Preparation can intern further classes (generic
        # parameters, runtime bases, mro entries) - iterate to a fixpoint.
        while True:
            pending = [
                obj
                for obj in self.__fullnames_by_type
                if isinstance(obj, type) and not self.is_info_prepared(obj)
            ]
            if not pending:
                break
            for obj in pending:
                reflector._prepare_runtime_type_info(obj, reflector._mirror.get_type_info(obj))  # noqa

        self.__is_frozen = True

    ##
    # hierarchy

    def has_parent(self) -> bool:
        return self.__parent is not None

    def compact(self) -> bool:
        if self.__parent is None:
            return False

        self.check_not_frozen()

        #

        fullnames_by_type: dict[object, str] = {}
        types_by_fullname: dict[str, object] = {}
        infos_by_fullname: dict[str, TypeInfo] = {}

        type_cache: dict[object, Type] = {}
        cached_types: set[Type] = set()

        prepared_infos: set[type] = set()

        runtime_aliases: dict[ta.TypeAliasType, TypeAlias] = {}

        relevant_namespaces = set[_RuntimeNamespace]()

        #

        def rec(cur: _MirrorState) -> None:
            if cur.__parent is not None:
                rec(cur.__parent)

            fullnames_by_type.update(cur.__fullnames_by_type)
            types_by_fullname.update(cur.__types_by_fullname)
            infos_by_fullname.update(cur.__infos_by_fullname)

            type_cache.update(cur.__type_cache)
            cached_types.update(cur.__cached_types)

            prepared_infos.update(cur.__prepared_infos)

            runtime_aliases.update(cur.__runtime_aliases)

            relevant_namespaces.update(cur.__relevant_namespaces)

        rec(self)

        #

        self.__parent = None

        self.__fullnames_by_type = fullnames_by_type
        self.__types_by_fullname = types_by_fullname
        self.__infos_by_fullname = infos_by_fullname

        self.__type_cache = type_cache
        self.__cached_types = cached_types

        self.__prepared_infos = prepared_infos

        self.__runtime_aliases = runtime_aliases

        self.__relevant_namespaces = relevant_namespaces

        return True

    ##
    # accessors

    def get_fullname_for_type(self, obj: object) -> str | None:
        if (fullname := self.__fullnames_by_type.get(obj)) is not None:
            return fullname

        if self.__parent is not None:
            return self.__parent.get_fullname_for_type(obj)

        return None

    def get_type_for_fullname(self, fullname: str) -> object | None:
        if (obj := self.__types_by_fullname.get(fullname)) is not None:
            return obj

        if self.__parent is not None:
            return self.__parent.get_type_for_fullname(fullname)

        return None

    def intern_type_fullname(self, obj: object, fullname: str) -> None:
        self.check_not_frozen()

        self.__fullnames_by_type[obj] = fullname
        self.__types_by_fullname[fullname] = obj

    #

    def get_info(self, fullname: str) -> TypeInfo | None:
        if (info := self.__infos_by_fullname.get(fullname)) is not None:
            return info

        if self.__parent is not None:
            return self.__parent.get_info(fullname)

        return None

    def put_info(self, fullname: str, info: TypeInfo) -> None:
        self.check_not_frozen()

        self.__infos_by_fullname[fullname] = info

    #

    def is_info_prepared(self, origin: type) -> bool:
        if origin in self.__prepared_infos:
            return True

        if self.__parent is not None:
            return self.__parent.is_info_prepared(origin)

        return False

    def mark_info_prepared(self, origin: type) -> None:
        self.check_not_frozen()

        self.__prepared_infos.add(origin)

    #

    def get_cached_reflected_type(self, obj: object) -> Type | None:
        try:
            return self.__type_cache[obj]
        except KeyError:
            pass
        except TypeError:
            return None

        if self.__parent is not None:
            return self.__parent.get_cached_reflected_type(obj)

        return None

    def cache_reflected_type(self, obj: object, typ: Type) -> None:
        self.check_not_frozen()

        try:
            self.__type_cache[obj] = typ
        except TypeError:
            return
        self.__cached_types.add(typ)

    #

    def get_runtime_alias(self, obj: ta.TypeAliasType) -> TypeAlias | None:
        if (alias := self.__runtime_aliases.get(obj)) is not None:
            return alias

        if self.__parent is not None:
            return self.__parent.get_runtime_alias(obj)

        return None

    def put_runtime_alias(self, obj: ta.TypeAliasType, alias: TypeAlias) -> None:
        self.check_not_frozen()

        self.__runtime_aliases[obj] = alias
        self.__unresolved_aliases.add(obj)

    def is_alias_unresolved(self, obj: ta.TypeAliasType) -> bool:
        # No chain walk: a frozen parent can hold no unresolved aliases - freeze() heals or fails.
        return obj in self.__unresolved_aliases

    def mark_alias_resolved(self, obj: ta.TypeAliasType) -> None:
        self.check_not_frozen()

        self.__unresolved_aliases.discard(obj)

    #

    def new_type_var_id(self) -> TypeVarId:
        self.check_not_frozen()

        type_var_id = TypeVarId(self.__next_type_var_id, namespace=self.__type_var_namespace.name)
        self.__next_type_var_id += 1
        return type_var_id


class _InternalMirror:
    def __init__(
            self,
            *,
            forward_ref_resolver: ForwardRefResolver | None = None,
            unresolved_forward_ref_policy: UnresolvedForwardRefPolicy | None = None,
            type_reflect_substitutor: TypeReflectSubstitutor | None = None,

            parent_state: _MirrorState | None = None,
    ) -> None:
        super().__init__()

        if unresolved_forward_ref_policy is None:
            unresolved_forward_ref_policy = DEFAULT_UNRESOLVED_FORWARD_REF_POLICY
        elif unresolved_forward_ref_policy not in ('raise', 'unbound'):
            raise ReflectionValueError(f'Unsupported unresolved forward ref policy: {unresolved_forward_ref_policy!r}')

        self.forward_ref_resolver = forward_ref_resolver
        self.unresolved_forward_ref_policy = unresolved_forward_ref_policy
        self.type_reflect_substitutor = type_reflect_substitutor

        #

        self._state = _MirrorState(
            parent=parent_state,
        )

    ##
    # freezing

    def freeze(self) -> None:
        self._state.freeze(_TypeReflector(self))

    ##
    # symbols

    def _make_dynamic_type_name_hint(self, obj: type) -> str:
        module = getattr(obj, '__module__', None)
        qualname = getattr(obj, '__qualname__', None)
        if isinstance(module, str) and module and isinstance(qualname, str) and qualname:
            return qualname if module == 'builtins' else f'{module}.{qualname}'

        name = getattr(obj, '__name__', None)
        if isinstance(name, str) and name:
            return name

        return 'type'

    def _make_dynamic_type_fullname(self, obj: type) -> str:
        return f'{self._make_dynamic_type_name_hint(obj)}@{id(obj):x}'

    def _make_newtype_fullname(self, obj: object) -> str:
        module = getattr(obj, '__module__', None)
        qualname = getattr(obj, '__qualname__', None)
        if isinstance(module, str) and module and isinstance(qualname, str) and qualname:
            return qualname if module == 'builtins' else f'{module}.{qualname}'

        name = getattr(obj, '__name__', None)
        if isinstance(name, str) and name:
            return name

        return f'NewType@{id(obj):x}'

    def _make_type_var(
            self,
            fullname: str,
            index: int,
            variance: VarianceKind,
    ) -> TypeVarType:
        object_info = self.get_type_info('builtins.object')
        object_type = Instance(object_info, ())
        default = _ANY_TYPES[TypeOfAny.FROM_OMITTED_GENERICS]
        name = f'T{index}'
        return TypeVarType(
            name,
            f'{fullname}.{name}',
            TypeVarId(index + 1),
            (),
            object_type,
            default,
            variance,
        )

    def _make_type_info(
            self,
            fullname: str,
            *,
            runtime_object: object | None = None,
    ) -> TypeInfo:
        name = fullname.rsplit('.', 1)[-1]
        known = _KNOWNS_BY_FULLNAME.get(fullname)
        arity = known.arity if known is not None and known.arity is not None else 0
        if known is not None and known.variances is not None:
            variances = list(known.variances)
        else:
            variances = [VarianceKind.IN] * arity
        type_vars: list[TypeVarLikeType] = [
            self._make_type_var(fullname, index, variance)
            for index, variance in enumerate(variances)
        ]
        return TypeInfo(
            name,
            fullname,
            type_vars=type_vars,
            variances=variances,
            runtime_object=runtime_object,
        )

    def _make_known_bases(self, info: TypeInfo) -> ta.Sequence[Type]:
        if (known := _KNOWNS_BY_FULLNAME.get(info._fullname)) is not None:
            specs = known.specs or ()
        else:
            specs = ()
        bases: list[Type] = []
        for target_fullname, arg_specs in specs:
            bases.append(Instance(
                self.get_type_info(target_fullname),
                [
                    self._make_known_base_arg(info, arg_spec)
                    for arg_spec in arg_specs
                ],
            ))
        return bases

    def _make_known_base_arg(self, info: TypeInfo, arg_spec: _KnownBaseArg) -> Type:
        if isinstance(arg_spec, int):
            return info.type_vars[arg_spec]
        return Instance(self.get_type_info(arg_spec), ())

    def _make_known_mro(self, info: TypeInfo) -> ta.Sequence[TypeInfo] | None:
        if (known := _KNOWNS_BY_FULLNAME.get(info._fullname)) is None or (tail := known.mro_tail) is None:
            return None
        return [info, *[self.get_type_info(fullname) for fullname in tail]]

    #

    def get_cached_type_info(self, obj: type | str | ta.NewType) -> TypeInfo | None:
        if isinstance(obj, str):
            return self._state.get_info(obj)

        if (fullname := self._state.get_fullname_for_type(obj)) is None:
            return None

        # NOTE: This is racy with `get_type_info` below - this runs without any lock, and `_fullnames_by_type` will be
        # populated before `_infos_by_fullname` - if this does happen it'll just be retried under the lock.
        return self._state.get_info(fullname)

    #

    def get_type_info(self, obj: type | str) -> TypeInfo:
        runtime_object: object
        if isinstance(obj, str):
            fullname = obj
            runtime_object = None
        else:
            runtime_object = obj
            if (ex_fullname := self._state.get_fullname_for_type(obj)) is not None:
                fullname = ex_fullname
            else:
                fullname = self._make_dynamic_type_fullname(obj)
                if (ex_ty := self._state.get_type_for_fullname(fullname)) is not None:
                    raise ReflectionValueError(
                        f'Dynamic fullname {fullname!r} for type {obj!r} already used by type {ex_ty!r}',
                    )
                self._state.intern_type_fullname(obj, fullname)

        if (ex_info := self._state.get_info(fullname)) is not None:
            return ex_info

        if runtime_object is None:
            runtime_object = self._state.get_type_for_fullname(fullname)

        info = self._make_type_info(
            fullname,
            runtime_object=runtime_object,
        )
        self._state.put_info(fullname, info)
        info._bases = tuple(self._make_known_bases(info))
        if (mro := self._make_known_mro(info)) is not None:
            info._mro = tuple(mro)
        if (
                runtime_object is not None and
                isinstance(runtime_object, type) and
                issubclass(runtime_object, enum.Enum)
        ):
            info._is_enum = True
            info._enum_members = tuple(
                member.name
                for member in runtime_object
            )
        return info

    #

    def get_newtype_info(self, obj: object, *, reflector: _TypeReflector | None = None) -> TypeInfo:
        if not isinstance(obj, ta.NewType):  # noqa
            raise TypeError('get_newtype_info only accepts `typing.NewType` objects')

        if (ex_fullname := self._state.get_fullname_for_type(obj)) is not None:
            fullname = ex_fullname
        else:
            fullname = self._make_newtype_fullname(obj)
            if self._state.get_type_for_fullname(fullname) is not None:
                fullname = f'{fullname}@{id(obj):x}'
            self._state.intern_type_fullname(obj, fullname)

        if (ex_info := self._state.get_info(fullname)) is not None:
            return ex_info

        name = fullname.rsplit('.', 1)[-1]
        info = TypeInfo(
            name,
            fullname,
            runtime_object=obj,
        )

        # Cached before supertype reflection so self-referential supertypes (via forward refs) resolve to this info.
        self._state.put_info(fullname, info)

        if reflector is None:
            reflector = _TypeReflector(self)
        supertype = reflector.reflect_newtype_supertype(obj)

        info._newtype_supertype = supertype

        if isinstance(supertype, Instance):
            base = supertype
        else:
            base = Instance(self.get_type_info('builtins.object'), ())
        info._bases = (base,)
        info._mro = (info, *base._type._mro)

        return info

    ##
    # types

    def is_uncacheable_reflect_type(self, obj: object) -> bool:
        # Forward-ref resolution is context-dependent (see _reflect_forward_ref): the same ForwardRef / str resolves
        # differently depending on the owner scope in which it appears, and distinct ForwardRefs sharing a name compare
        # and hash equal. Never read or write the shared cache under such an ambiguous key.
        if _is_forward_ref(obj):
            return True

        return False

    def reflect_type(self, obj: object, *, skip_substitution: bool = False) -> Type:
        return _TypeReflector(self).reflect_type(obj, skip_substitution=skip_substitution)


class _TypeReflector:
    def __init__(self, mirror: _InternalMirror) -> None:
        super().__init__()

        self._mirror = mirror

        #

        self._resolving_type_aliases, self._type_alias_stack = set(), []
        self._resolving_forward_refs, self._forward_ref_owner_stack = set(), []

    _resolving_type_aliases: set[ta.TypeAliasType]
    _type_alias_stack: list[ta.TypeAliasType]

    _resolving_forward_refs: set[str]
    _forward_ref_owner_stack: list[object]

    #

    def reflect_type(self, obj: object, *, skip_substitution: bool = False) -> Type:
        # Substitution applies at every level of descent. The substituted result is deliberately not re-substituted
        # (see ReflectSubstitutor), and reflection proceeds - including caching - under the substituted object.
        if not skip_substitution and (substitutor := self._mirror.type_reflect_substitutor) is not None:
            if (substituted := substitutor(obj)) is not None and substituted is not obj:
                obj = substituted

        if self._mirror.is_uncacheable_reflect_type(obj):
            return self._reflect_type_uncached(obj)

        if (cached := self._mirror._state.get_cached_reflected_type(obj)) is not None:
            return cached

        typ = self._reflect_type_uncached(obj)

        # A frozen mirror can still statelessly reflect compositions of the symbols it already holds - the memo write
        # is the only mutation such a reflection would perform, so it is simply skipped.
        if not self._mirror._state.is_frozen:
            self._mirror._state.cache_reflected_type(obj, typ)

        return typ

    #

    _CAN_REFLECT_OBJECT_IDS: ta.Final[ta.Mapping[int, ta.Any]] = {id(obj): obj for obj in [
        ta.Any,
        ta.Never,
        ta.NoReturn,
    ]}

    _CAN_REFLECT_OBJECT_TYPES: ta.Final[tuple[type, ...]] = (
        ta.TypeAliasType,
        ta.TypeVar,
        ta.ParamSpec,
        ta.TypeVarTuple,
        type,
    )

    _CAN_REFLECT_OBJECT_PREDICATES: ta.Final[ta.Sequence[ta.Callable[[object], bool]]] = (
        _is_none_type,
        _is_forward_ref,
        _is_newtype,
        _is_typed_dict_class,
    )

    @classmethod
    def can_reflect_type(cls, obj: object) -> bool:
        return (
            id(obj) in cls._CAN_REFLECT_OBJECT_IDS or
            isinstance(obj, cls._CAN_REFLECT_OBJECT_TYPES) or
            ta.get_origin(obj) is not None or
            any(fn(obj) for fn in cls._CAN_REFLECT_OBJECT_PREDICATES)
        )

    #

    def _reflect_type_uncached(self, obj: object) -> Type:
        if obj is ta.Any:
            return _ANY_TYPES[TypeOfAny.EXPLICIT]

        if obj is ta.Never or obj is ta.NoReturn:
            return _UNINHABITED_TYPE

        if _is_none_type(obj):
            return _NONE_TYPE

        if _is_forward_ref(obj):
            return self._reflect_forward_ref(obj)  # type: ignore[arg-type]

        if isinstance(obj, ta.TypeAliasType):
            return self._reflect_type_alias(obj, (), is_subscripted=False)

        if isinstance(obj, ta.TypeVar):
            return self._reflect_type_var(obj)

        if isinstance(obj, ta.ParamSpec):
            return self._reflect_param_spec(obj)

        if isinstance(obj, ta.TypeVarTuple):
            return self._reflect_type_var_tuple(obj)

        if _is_newtype(obj):
            return self._reflect_newtype(obj)

        origin = ta.get_origin(obj)

        if origin is not None:
            args = ta.get_args(obj)

            if origin is ta.Annotated:
                return self._reflect_annotated(args)

            if origin is ta.ClassVar or origin is ta.Final:
                return self._reflect_single_arg_wrapper(origin, args)

            if origin is ta.Required:  # noqa
                return self._reflect_required(args, required=True)

            if origin is ta.NotRequired:  # noqa
                return self._reflect_required(args, required=False)

            if origin is ta.ReadOnly:  # noqa
                return self._reflect_read_only(args)

            if origin is ta.Unpack:
                return self._reflect_unpack(args)

            if origin is ta.TypeGuard:
                return self._reflect_type_guard(args)

            if origin is ta.TypeIs:
                raise UnreflectableTypeError(f'Unsupported TypeIs runtime type object: {obj!r}')

            if origin is ta.Literal:
                return self._reflect_literal(args)

            if origin is ta.Union or origin is pytypes.UnionType:
                return self._reflect_union(args)

            if origin is cabc.Callable:
                return self._reflect_callable(args)

            if origin is type:
                return self._reflect_type_type(args)

            if origin is tuple:
                return self._reflect_tuple(args)

            if isinstance(origin, ta.TypeAliasType):
                return self._reflect_type_alias(origin, args, is_subscripted=True)

            if _is_typed_dict_class(origin):
                return self._reflect_typed_dict(origin, args)

            return self._reflect_instance(origin, args)

        if _is_typed_dict_class(obj):
            return self._reflect_typed_dict(obj, ())  # type: ignore[arg-type]

        if isinstance(obj, type):
            return self._reflect_instance(obj, ())

        raise UnreflectableTypeError(f'Unsupported runtime type object: {obj!r}')

    class _PushedForwardRefOwner:
        def __init__(self, run: _TypeReflector, owner: object) -> None:
            self._run, self._owner = run, owner

        def __enter__(self) -> None:
            if self._owner is not None:
                self._run._forward_ref_owner_stack.append(self._owner)

        def __exit__(self, et, e, tb):
            if self._owner is not None:
                self._run._forward_ref_owner_stack.pop()

    def _pushed_forward_ref_owner(self, owner: object) -> ta.ContextManager[None]:
        return self._PushedForwardRefOwner(self, owner)

    def _forward_ref_module_owner(self, obj: object) -> object | None:
        module_name = getattr(obj, '__module__', None)
        if not isinstance(module_name, str) or not module_name:
            return None
        return sys.modules.get(module_name)

    def _reflect_forward_ref(self, obj: str | annotationlib.ForwardRef) -> Type:
        if isinstance(obj, str):
            name = obj
        else:
            name = obj.__forward_arg__

        # The type alias stack always takes precedence - a forward reference naming an in-progress alias (or a
        # subscription of one) resolves structurally, ahead of any resolver or owner scope.
        for alias_obj in reversed(self._type_alias_stack):
            if name == alias_obj.__name__:
                return TypeAliasType(self._get_type_alias_symbol(alias_obj), ())
            if (alias_ref := self._reflect_type_alias_forward_ref(name, alias_obj)) is not None:
                return alias_ref

        if name in self._resolving_forward_refs:
            raise UnreflectableTypeError(f'Recursive forward reference resolution: {name!r}')

        self._resolving_forward_refs.add(name)
        try:
            try:
                resolved = self._resolve_forward_ref(obj, name)
            except UnreflectableTypeError:
                # A forward reference we could not bind via the alias stack, a resolver, or an owner scope. Under the
                # 'unbound' policy we degrade to a first-class UnboundType leaf (retaining the original ForwardRef for
                # identity) rather than failing. A recursion-guard violation is a distinct pathology and is *not* caught
                # here (it is raised before we reach this point).
                if self._mirror.unresolved_forward_ref_policy == 'unbound':
                    return self._unbound_forward_ref(obj, name)
                raise
            return self.reflect_type(resolved)
        finally:
            self._resolving_forward_refs.remove(name)

    def _unbound_forward_ref(self, obj: str | annotationlib.ForwardRef, name: str) -> UnboundType:
        runtime_object = obj if isinstance(obj, annotationlib.ForwardRef) else None
        return UnboundType(
            name,
            runtime_object=runtime_object,
        )

    def _resolve_forward_ref(self, obj: str | annotationlib.ForwardRef, name: str) -> object:
        def resolve() -> object:
            return self._resolve_forward_ref_in_owner(obj, name)

        # When a resolver is supplied it owns the resolution policy: it is handed the full context - including the
        # `resolve` closure that performs the default owner-scope resolution - and decides how to combine them. When no
        # resolver is supplied the default owner-scope resolution runs directly.
        if self._mirror.forward_ref_resolver is not None:
            return self._mirror.forward_ref_resolver(ForwardRefResolution(obj, name, resolve))

        return resolve()

    def _resolve_forward_ref_in_owner(self, obj: str | annotationlib.ForwardRef, name: str) -> object:
        if not self._forward_ref_owner_stack:
            raise UnreflectableTypeError(f'Unsupported unresolved forward reference: {obj!r}')

        owner = self._forward_ref_owner_stack[-1]

        if isinstance(obj, annotationlib.ForwardRef):
            forward_ref = obj
        else:
            forward_ref = annotationlib.ForwardRef(name)

        try:
            return ta.evaluate_forward_ref(forward_ref, owner=owner)
        except NameError as e:
            raise UnreflectableTypeError(f'Unsupported unresolved forward reference: {obj!r}') from e

    def _reflect_type_alias_forward_ref(
            self,
            name: str,
            obj: ta.TypeAliasType,
    ) -> TypeAliasType | None:
        prefix = f'{obj.__name__}['
        if not name.startswith(prefix) or not name.endswith(']'):
            return None

        parameter_names = {
            type_param.__name__: type_param
            for type_param in obj.__type_params__
        }
        arg_names = [arg.strip() for arg in name[len(prefix):-1].split(',')]
        if not arg_names or any(not arg_name for arg_name in arg_names):
            raise UnreflectableTypeError(f'Unsupported type alias forward reference: {name!r}')

        try:
            args = [self._reflect_type_alias_forward_ref_arg(arg_name, parameter_names) for arg_name in arg_names]
        except KeyError as e:
            raise UnreflectableTypeError(f'Unsupported type alias forward reference: {name!r}') from e

        return TypeAliasType(self._get_type_alias_symbol(obj), args)

    def _make_tuple_fallback(self) -> Instance:
        return Instance(self._mirror.get_type_info(tuple), [_make_any()])

    def _reflect_type_alias_forward_ref_arg(
            self,
            name: str,
            parameter_names: ta.Mapping[str, object],
    ) -> Type:
        if not name.startswith('*'):
            return self.reflect_type(parameter_names[name])

        parameter = parameter_names[name[1:]]
        if not isinstance(parameter, ta.TypeVarTuple):
            raise KeyError(name)

        type_var_tuple = self.reflect_type(parameter)
        if not isinstance(type_var_tuple, TypeVarTupleType):
            raise KeyError(name)

        return TupleType(
            [UnpackType(type_var_tuple)],
            self._make_tuple_fallback(),
        )

    def _reflect_type_alias(
            self,
            obj: ta.TypeAliasType,
            args: tuple[object, ...],
            *,
            is_subscripted: bool,
    ) -> Type:
        type_params = obj.__type_params__

        alias = self._get_type_alias_symbol(obj)
        alias_args = self._reflect_type_alias_args(obj, type_params, args, is_subscripted=is_subscripted)

        return TypeAliasType(alias, alias_args)

    def _reflect_variadic_type_args(
            self,
            obj_kind: str,
            obj: ta.Any,
            type_params: ta.Sequence[object],
            args: ta.Sequence[object],
            variadic_index: int,
    ) -> list[Type]:
        prefix_len = variadic_index
        suffix_len = len(type_params) - variadic_index - 1
        if len(args) < prefix_len + suffix_len:
            raise UnreflectableTypeError(f'Unsupported {obj_kind} arguments for {obj!r}: {args!r}')

        reflected_args: list[Type] = []
        reflected_args.extend(self.reflect_type(arg) for arg in args[:prefix_len])

        variadic_start = prefix_len
        variadic_end = len(args) - suffix_len
        reflected_args.append(TupleType(
            [self.reflect_type(arg) for arg in args[variadic_start:variadic_end]],
            self._make_tuple_fallback(),
        ))

        if suffix_len:
            reflected_args.extend(self.reflect_type(arg) for arg in args[-suffix_len:])

        return reflected_args

    def _reflect_type_alias_args(
            self,
            obj: ta.TypeAliasType,
            type_params: tuple[object, ...],
            args: tuple[object, ...],
            *,
            is_subscripted: bool,
    ) -> list[Type]:
        if not args and not is_subscripted:
            return []

        type_var_tuple_indexes = [
            index
            for index, type_param in enumerate(type_params)
            if isinstance(type_param, ta.TypeVarTuple)
        ]
        if not type_var_tuple_indexes:
            if len(args) != len(type_params):
                raise UnreflectableTypeError(f'Unsupported type alias arguments for {obj!r}: {args!r}')
            return [self.reflect_type(arg) for arg in args]

        if len(type_var_tuple_indexes) > 1:
            raise UnreflectableTypeError(f'Unsupported type alias with multiple TypeVarTuple parameters: {obj!r}')

        variadic_index = type_var_tuple_indexes[0]
        return self._reflect_variadic_type_args(
            'type alias',
            obj,
            type_params,
            args,
            variadic_index,
        )

    def _get_type_alias_symbol(self, obj: ta.TypeAliasType) -> TypeAlias:
        if (alias := self._mirror._state.get_runtime_alias(obj)) is None:
            type_params = obj.__type_params__
            alias = TypeAlias(
                obj.__name__,
                _make_any(),
                fullname=f'{obj.__module__}.{obj.__name__}',
                alias_tvars=[
                    self._reflect_type_var_like_parameter(type_param)
                    for type_param in type_params
                ],
                runtime_object=obj,
            )
            self._mirror._state.put_runtime_alias(obj, alias)

        # Target resolution happens exactly once per symbol (on success) - not per reflection. A symbol whose runtime
        # alias is currently mid-resolution is returned as-is: its occurrences are recursive references.
        if self._mirror._state.is_alias_unresolved(obj) and obj not in self._resolving_type_aliases:
            self._resolve_type_alias_target(obj, alias)

        return alias

    def _resolve_type_alias_target(self, obj: ta.TypeAliasType, alias: TypeAlias) -> None:
        self._resolving_type_aliases.add(obj)
        self._type_alias_stack.append(obj)
        try:
            target = self.reflect_type(obj.__value__)
        finally:
            self._type_alias_stack.pop()
            self._resolving_type_aliases.remove(obj)

        alias._target = target
        self._mirror._state.mark_alias_resolved(obj)

        # Concretize recursiveness eagerly - the lazy `TypeAliasType.is_recursive` computation would otherwise mutate
        # the symbol on first read, arbitrarily later. Direct self-reference is caught by the computed check, mutual
        # recursion (an enclosing alias still mid-resolution occurring in this target) by the second.
        if TypeAliasType(alias, ()).is_recursive or self._contains_resolving_type_alias(target):
            alias._is_recursive = True

    def _contains_resolving_type_alias(self, typ: Type) -> bool:
        active_aliases = {
            alias
            for obj in self._resolving_type_aliases
            if (alias := self._mirror._state.get_runtime_alias(obj)) is not None
        }
        if not active_aliases:
            return False
        return _contains_any_type_alias(typ, active_aliases, set())

    def reflect_newtype_supertype(self, obj: object) -> Type:
        # A newtype's supertype may contain forward references that resolve in the module in which the newtype was
        # defined - which need not be the module of whatever is currently being reflected.
        with self._pushed_forward_ref_owner(self._forward_ref_module_owner(obj)):
            return self.reflect_type(getattr(obj, '__supertype__'))

    def _reflect_newtype(self, obj: object) -> Instance:
        return Instance(self._mirror.get_newtype_info(obj, reflector=self), ())

    def _reflect_annotated(self, args: tuple[object, ...]) -> AnnotatedType:
        if len(args) < 2:
            raise UnreflectableTypeError(f'Unsupported Annotated arguments: {args!r}')

        return AnnotatedType(self.reflect_type(args[0]), tuple(args[1:]))

    def _reflect_type_guard(self, args: tuple[object, ...]) -> TypeGuardedType:
        if len(args) != 1:
            raise UnreflectableTypeError(f'Unsupported TypeGuard arguments: {args!r}')

        return TypeGuardedType(self.reflect_type(args[0]))

    def _reflect_required(self, args: tuple[object, ...], *, required: bool) -> RequiredType:
        if len(args) != 1:
            raise UnreflectableTypeError(f'Unsupported Required arguments: {args!r}')

        return RequiredType(self.reflect_type(args[0]), required=required)

    def _reflect_read_only(self, args: tuple[object, ...]) -> ReadOnlyType:
        if len(args) != 1:
            raise UnreflectableTypeError(f'Unsupported ReadOnly arguments: {args!r}')

        return ReadOnlyType(self.reflect_type(args[0]))

    def _reflect_unpack(self, args: tuple[object, ...]) -> UnpackType:
        if len(args) != 1:
            raise UnreflectableTypeError(f'Unsupported Unpack arguments: {args!r}')

        return UnpackType(self.reflect_type(args[0]))

    def _reflect_typed_dict(self, origin: type, args: tuple[object, ...]) -> TypedDictType:
        parameters = getattr(origin, '__parameters__', ())
        if len(args) != len(parameters):
            raise UnreflectableTypeError(f'Unsupported TypedDict arguments for {origin!r}: {args!r}')

        # Forward references in a TypedDict's item annotations resolve in the TypedDict class's module scope.
        with self._pushed_forward_ref_owner(origin):
            replacements = {
                self._reflect_type_var_parameter(parameter): self.reflect_type(arg)
                for parameter, arg in zip(parameters, args)
            }

            required_keys = set(getattr(origin, '__required_keys__'))
            readonly_keys = set(getattr(origin, '__readonly_keys__', frozenset()))
            annotations = getattr(origin, '__annotations__')
            if not isinstance(annotations, dict):
                raise UnreflectableTypeError(f'Unsupported TypedDict annotations for {origin!r}: {annotations!r}')

            items: dict[str, Type] = {}
            for name, annotation in annotations.items():
                item = self.reflect_type(annotation)
                if replacements:
                    item = substitute_type(item, replacements)
                items[name] = self._unwrap_typed_dict_item(item)

            fallback = self._reflect_instance(dict, (str, object))
            return TypedDictType(items, required_keys, readonly_keys, fallback)

    def _unwrap_typed_dict_item(self, typ: Type) -> Type:
        seen_required = False
        seen_readonly = False

        while isinstance(typ, (RequiredType, ReadOnlyType)):
            if isinstance(typ, RequiredType):
                if seen_required:
                    raise UnreflectableTypeError('Unsupported nested Required or NotRequired TypedDict item')
                seen_required = True

            elif isinstance(typ, ReadOnlyType):
                if seen_readonly:
                    raise UnreflectableTypeError('Unsupported nested ReadOnly TypedDict item')
                seen_readonly = True

            typ = typ._item

        if typ.accept(_HasTypedDictItemWrapper()):
            raise UnreflectableTypeError('Unsupported nested TypedDict item wrapper')

        return typ

    def _reflect_instance(self, origin: type, args: tuple[object, ...]) -> Instance:
        info = self._mirror.get_type_info(origin)
        self._prepare_runtime_type_info(origin, info)
        reflected_args = self._reflect_instance_args(origin, info, args)

        if len(reflected_args) < len(info.type_vars):
            reflected_args.extend(_make_any() for _ in range(len(info.type_vars) - len(reflected_args)))

        return Instance(info, reflected_args)

    def _reflect_instance_args(
            self,
            origin: type,
            info: TypeInfo,
            args: tuple[object, ...],
    ) -> list[Type]:
        type_vars = info._type_vars
        if not args:
            return []

        type_var_tuple_indexes = [
            index
            for index, type_var in enumerate(type_vars)
            if isinstance(type_var, TypeVarTupleType)
        ]
        if not type_var_tuple_indexes:
            if len(args) > len(type_vars):
                raise UnreflectableTypeError(f'Unsupported generic arguments for {origin!r}: {args!r}')
            return [self.reflect_type(arg) for arg in args]

        if len(type_var_tuple_indexes) > 1:
            raise UnreflectableTypeError(f'Unsupported generic class with multiple TypeVarTuple parameters: {origin!r}')

        variadic_index = type_var_tuple_indexes[0]
        return self._reflect_variadic_type_args(
            'generic',
            origin,
            type_vars,
            args,
            variadic_index,
        )

    def _prepare_runtime_type_info(self, origin: type, info: TypeInfo) -> None:
        if self._mirror._state.is_info_prepared(origin):
            return
        self._mirror._state.mark_info_prepared(origin)

        # Forward references in a class's parameters' bounds or in its runtime bases resolve in that class's module
        # scope. (A parameter type var carrying its own module overrides this while its bound is reflected.)
        with self._pushed_forward_ref_owner(origin):
            parameters = getattr(origin, '__parameters__', ())
            if parameters and not info._type_vars:
                info._type_vars = tuple(
                    self._reflect_type_var_like_parameter(parameter)
                    for parameter in parameters
                )
                info._variances = tuple(
                    type_var._variance if isinstance(type_var, TypeVarType) else VarianceKind.IN
                    for type_var in info.type_vars
                )

            mro = getattr(origin, '__mro__', None)
            if mro is not None and info._mro == (info,):
                info._mro = tuple(
                    self._mirror.get_type_info(cls)
                    for cls in mro
                    if isinstance(cls, type)
                )

            if info._bases:
                return

            runtime_bases = _get_runtime_bases(origin)
            info._bases = tuple(
                self._reflect_runtime_base(base)
                for base in runtime_bases
            )

    def _reflect_type_var_parameter(self, obj: object) -> TypeVarType:
        type_var = self.reflect_type(obj)
        if not isinstance(type_var, TypeVarType):
            raise UnreflectableTypeError(f'Unsupported generic parameter: {obj!r}')
        return type_var

    def _reflect_type_var_like_parameter(self, obj: object) -> TypeVarLikeType:
        type_var_like = self.reflect_type(obj)
        if not isinstance(type_var_like, TypeVarLikeType):
            raise UnreflectableTypeError(f'Unsupported generic parameter: {obj!r}')
        return type_var_like

    def _reflect_param_spec_parameter(self, obj: object) -> ParamSpecType:
        param_spec = self.reflect_type(obj)
        if not isinstance(param_spec, ParamSpecType):
            raise UnreflectableTypeError(f'Unsupported ParamSpec parameter: {obj!r}')
        return param_spec

    def _reflect_runtime_base(self, obj: object) -> Instance:
        base = self.reflect_type(obj)
        if not isinstance(base, Instance):
            raise UnreflectableTypeError(f'Unsupported runtime base: {obj!r}')
        return base

    def _reflect_tuple(self, args: tuple[object, ...]) -> Type:
        info = self._mirror.get_type_info(tuple)

        if len(args) == 2 and args[1] is Ellipsis:
            return Instance(info, [self.reflect_type(args[0])])

        fallback = Instance(info, [_make_any()])
        return TupleType([self.reflect_type(arg) for arg in args], fallback)

    def _reflect_single_arg_wrapper(self, origin: object, args: tuple[object, ...]) -> Type:
        if len(args) != 1:
            raise UnreflectableTypeError(f'Unsupported wrapper arguments for {origin!r}: {args!r}')

        return self.reflect_type(args[0])

    def _reflect_type_type(self, args: tuple[object, ...]) -> TypeType:
        if len(args) != 1:
            raise UnreflectableTypeError(f'Unsupported type arguments: {args!r}')

        return TypeType(self.reflect_type(args[0]))

    def _reflect_union(self, args: tuple[object, ...]) -> Type:
        return make_union([self.reflect_type(arg) for arg in args])

    def _reflect_callable(self, args: tuple[object, ...]) -> CallableType:
        fallback = Instance(
            self._mirror.get_type_info(cabc.Callable),  # type: ignore[arg-type]
            [_make_any()],
        )

        if len(args) != 2:
            raise UnreflectableTypeError(f'Unsupported Callable arguments: {args!r}')

        arg_spec, ret_type = args
        if arg_spec is Ellipsis:
            return CallableType(
                (),
                (),
                (),
                self.reflect_type(ret_type),
                fallback,
                is_ellipsis_args=True,
            )

        if isinstance(arg_spec, ta.ParamSpec):
            param_spec = self._reflect_param_spec_parameter(arg_spec)
            return CallableType(
                [param_spec, param_spec],
                [ArgKind.STAR, ArgKind.STAR2],
                [None, None],
                self.reflect_type(ret_type),
                fallback,
                variables=[param_spec],
            )

        if ta.get_origin(arg_spec) is ta.Concatenate:
            concatenate_args = ta.get_args(arg_spec)
            if len(concatenate_args) < 2 or not isinstance(concatenate_args[-1], ta.ParamSpec):
                raise UnreflectableTypeError(f'Unsupported Concatenate argument specification: {arg_spec!r}')

            param_spec = self._reflect_param_spec_parameter(concatenate_args[-1])
            prefix_types = [self.reflect_type(arg) for arg in concatenate_args[:-1]]
            return CallableType(
                [*prefix_types, param_spec, param_spec],
                [*[ArgKind.POS for _ in prefix_types], ArgKind.STAR, ArgKind.STAR2],
                [*[None for _ in prefix_types], None, None],
                self.reflect_type(ret_type),
                fallback,
                variables=[param_spec],
            )

        if not isinstance(arg_spec, list):
            raise UnreflectableTypeError(f'Unsupported Callable argument specification: {arg_spec!r}')

        arg_types = [self.reflect_type(arg) for arg in arg_spec]
        return CallableType(
            arg_types,
            [ArgKind.POS for _ in arg_types],
            [None for _ in arg_types],
            self.reflect_type(ret_type),
            fallback,
        )

    def _reflect_literal(self, args: tuple[object, ...]) -> Type:
        items = [self._reflect_literal_value(arg) for arg in args]
        if len(items) == 1:
            return items[0]
        return make_union(items)

    def _reflect_literal_value(self, obj: object) -> LiteralType:
        if isinstance(obj, enum.Enum):
            fallback = Instance(self._mirror.get_type_info(obj.__class__), ())
            return LiteralType(obj.name, fallback)

        if not _is_literal_value(obj):
            raise UnreflectableTypeError(f'Unsupported literal value: {obj!r}')

        fallback = Instance(self._mirror.get_type_info(type(obj)), ())
        return LiteralType(ta.cast(LiteralValue, obj), fallback)

    def _reflect_type_var(self, obj: ta.TypeVar) -> TypeVarType:
        if obj.__covariant__:
            variance = VarianceKind.CO
        elif obj.__contravariant__:
            variance = VarianceKind.CONTRA
        else:
            variance = VarianceKind.IN

        # A type var's bound / constraints / default may contain forward references that resolve in the module in which
        # the type var was defined - which need not be the module of whatever generic is currently being reflected.
        with self._pushed_forward_ref_owner(self._forward_ref_module_owner(obj)):
            bound = obj.__bound__
            if bound is None:
                upper_bound: Type = Instance(self._mirror.get_type_info(object), ())
            else:
                upper_bound = self.reflect_type(bound)

            default_obj = getattr(obj, '__default__', ta.NoDefault)
            if default_obj is ta.NoDefault:
                default: Type = _make_any()
            else:
                default = self.reflect_type(default_obj)

            values = [self.reflect_type(value) for value in obj.__constraints__]

        return TypeVarType(
            obj.__name__,
            obj.__name__,
            self._mirror._state.new_type_var_id(),
            values,
            upper_bound,
            default,
            variance,
            runtime_object=obj,
        )

    def _reflect_param_spec(self, obj: ta.ParamSpec) -> ParamSpecType:
        upper_bound = Instance(self._mirror.get_type_info(object), ())

        with self._pushed_forward_ref_owner(self._forward_ref_module_owner(obj)):
            default_obj = getattr(obj, '__default__', ta.NoDefault)
            if default_obj is ta.NoDefault:
                default: Type = _make_any()
            else:
                default = self.reflect_type(default_obj)

        return ParamSpecType(
            obj.__name__,
            obj.__name__,
            self._mirror._state.new_type_var_id(),
            upper_bound,
            default,
            runtime_object=obj,
        )

    def _reflect_type_var_tuple(self, obj: ta.TypeVarTuple) -> TypeVarTupleType:
        upper_bound = Instance(self._mirror.get_type_info(object), ())

        with self._pushed_forward_ref_owner(self._forward_ref_module_owner(obj)):
            default_obj = getattr(obj, '__default__', ta.NoDefault)
            if default_obj is ta.NoDefault:
                default: Type = _make_any()
            else:
                default = self.reflect_type(default_obj)

        tuple_fallback = Instance(self._mirror.get_type_info(tuple), [_make_any()])
        return TypeVarTupleType(
            obj.__name__,
            obj.__name__,
            self._mirror._state.new_type_var_id(),
            upper_bound,
            default,
            tuple_fallback,
            runtime_object=obj,
        )


##


class MirrorImpl(Mirror):
    def __init__(
            self,
            *,
            forward_ref_resolver: ForwardRefResolver | None = None,
            unresolved_forward_ref_policy: UnresolvedForwardRefPolicy | None = None,
            type_reflect_substitutor: TypeReflectSubstitutor | None = None,

            _parent_state: _MirrorState | None = None,
    ) -> None:
        super().__init__()

        self._lock = threading.RLock()

        self._internal = _InternalMirror(
            forward_ref_resolver=forward_ref_resolver,
            unresolved_forward_ref_policy=unresolved_forward_ref_policy,
            type_reflect_substitutor=type_reflect_substitutor,

            parent_state=_parent_state,
        )

        if _parent_state is None:
            for known in _KNOWNS:
                self.reflect_type(known.type)

    @property
    def forward_ref_resolver(self) -> ForwardRefResolver | None:
        return self._internal.forward_ref_resolver

    @property
    def unresolved_forward_ref_policy(self) -> UnresolvedForwardRefPolicy | None:
        return self._internal.unresolved_forward_ref_policy

    @property
    def type_reflect_substitutor(self) -> TypeReflectSubstitutor | None:
        return self._internal.type_reflect_substitutor

    #

    def get_type_info(self, obj: type | str | ta.NewType) -> TypeInfo:
        if (cached := self._internal.get_cached_type_info(obj)) is not None:
            return cached

        if self._internal._state.is_frozen:
            # Immutable - nothing to lock. Anything requiring new state raises FrozenMirrorReflectionError below.
            return self._get_type_info_uncached(obj)

        with self._lock:
            if (cached := self._internal.get_cached_type_info(obj)) is not None:
                return cached

            return self._get_type_info_uncached(obj)

    def _get_type_info_uncached(self, obj: type | str | ta.NewType) -> TypeInfo:
        if isinstance(obj, ta.NewType):
            return self._internal.get_newtype_info(obj)
        else:
            return self._internal.get_type_info(obj)

    def can_reflect_type(self, obj: object) -> bool:
        if (substitutor := self._internal.type_reflect_substitutor) is not None:
            if (substituted := substitutor(obj)) is not None and substituted is not obj:
                obj = substituted

        return isinstance(obj, (Type, type)) or _TypeReflector.can_reflect_type(obj)

    def reflect_type(self, obj: object) -> Type:
        if isinstance(obj, Type):
            return obj

        if (substitutor := self._internal.type_reflect_substitutor) is not None:
            if (substituted := substitutor(obj)) is not None and substituted is not obj:
                obj = substituted

        if not self._internal.is_uncacheable_reflect_type(obj):
            if (cached := self._internal._state.get_cached_reflected_type(obj)) is not None:
                return cached

        if self._internal._state.is_frozen:
            # Immutable - nothing to lock. Anything requiring new state raises FrozenMirrorReflectionError below.
            return self._internal.reflect_type(obj, skip_substitution=True)

        with self._lock:
            return self._internal.reflect_type(obj, skip_substitution=True)
