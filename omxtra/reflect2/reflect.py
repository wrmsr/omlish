# ruff: noqa: SLF001
import annotationlib
import collections.abc as cabc
import enum
import threading
import types as pytypes
import typing as ta

from .core.substitute import substitute_type
from .core.symbols import ArgKind
from .core.symbols import TypeAlias
from .core.symbols import TypeInfo
from .core.symbols import VarianceKind
from .core.typekeys import TypeKey
from .core.typekeys import alpha_structural_type_key
from .core.typekeys import alpha_structural_type_key_or_none
from .core.typekeys import alpha_type_key
from .core.typekeys import alpha_type_key_or_none
from .core.typekeys import structural_type_key
from .core.typekeys import structural_type_key_or_none
from .core.typekeys import type_key
from .core.typekeys import type_key_or_none
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
from .core.types import UnpackType
from .core.types import is_literal_value
from .core.typevisitor import BoolTypeQuery
from .core.typevisitor import BoolTypeQueryMode
from .errors import UnreflectableTypeError
from .universe import DEFAULT_UNIVERSE
from .universe import DynamicTypeNameSuffix
from .universe import RuntimeTypeUniverse


if ta.TYPE_CHECKING:
    from .annotations import TypeAliasAnnotationPolicy


ForwardRefResolver: ta.TypeAlias = ta.Callable[[str], object]


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


##


def _make_any() -> AnyType:
    return _ANY_TYPES[TypeOfAny.FROM_OMITTED_GENERICS]


def _make_tuple_fallback(universe: RuntimeTypeUniverse) -> Instance:
    return Instance(universe.get_type_info(tuple), [_make_any()])


def _is_none_type(obj: object) -> bool:
    return obj is None or obj is type(None)


def _is_literal_value(obj: object) -> bool:
    return is_literal_value(obj)


def _is_new_type(obj: object) -> bool:
    return isinstance(obj, ta.NewType)


def _is_forward_ref(obj: object) -> bool:
    return isinstance(obj, str | annotationlib.ForwardRef)


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


class RuntimeTypeReflector:
    def __init__(
            self,
            universe: RuntimeTypeUniverse | None = None,
            *,
            forward_ref_resolver: ForwardRefResolver | None = None,
    ) -> None:
        super().__init__()

        self._universe = DEFAULT_UNIVERSE if universe is None else universe
        self._forward_ref_resolver = forward_ref_resolver

        self._lock = threading.RLock()

        self._cache: dict[object, Type] = {}

        self._annotation_cache: dict[tuple[Type, str], object] = {}

        self._type_key_cache: dict[Type, TypeKey] = {}
        self._type_key_or_none_cache: dict[Type, TypeKey | None] = {}
        self._alpha_type_key_cache: dict[Type, TypeKey] = {}
        self._alpha_type_key_or_none_cache: dict[Type, TypeKey | None] = {}
        self._structural_type_key_cache: dict[Type, TypeKey] = {}
        self._structural_type_key_or_none_cache: dict[Type, TypeKey | None] = {}
        self._alpha_structural_type_key_cache: dict[Type, TypeKey] = {}
        self._alpha_structural_type_key_or_none_cache: dict[Type, TypeKey | None] = {}

        self._inspection_cache: dict[tuple[str, object], object] = {}

        self._runtime_type_params_by_type: dict[TypeVarLikeType, object] = {}
        self._runtime_aliases: dict[ta.TypeAliasType, TypeAlias] = {}
        self._resolving_type_aliases: set[ta.TypeAliasType] = set()
        self._type_alias_stack: list[ta.TypeAliasType] = []

        self._prepared_infos: set[type] = set()
        self._resolving_forward_refs: set[str] = set()

        self._type_var_namespace = f'runtime:{id(self):x}'
        self._next_type_var_id = 1

    @property
    def universe(self) -> RuntimeTypeUniverse:
        return self._universe

    @property
    def forward_ref_resolver(self) -> ForwardRefResolver | None:
        return self._forward_ref_resolver

    #

    def _reflect_type(self, obj: object) -> Type:
        try:
            return self._cache[obj]
        except KeyError:
            pass
        except TypeError:
            pass

        typ = self._reflect_type_uncached(obj)

        try:
            self._cache[obj] = typ
        except TypeError:
            pass

        return typ

    def reflect_type(self, obj: object) -> Type:
        try:
            return self._cache[obj]
        except KeyError:
            pass
        except TypeError:
            pass

        with self._lock:
            return self._reflect_type(obj)

    def _cached_inspection(
            self,
            kind: str,
            obj: object,
            factory: ta.Callable[[], object],
    ) -> object:
        key = (kind, obj)
        try:
            return self._inspection_cache[key]
        except KeyError:
            pass
        except TypeError:
            return factory()

        ret = factory()
        try:
            self._inspection_cache[key] = ret
        except TypeError:
            pass
        return ret

    def cached_inspection(
            self,
            kind: str,
            obj: object,
            factory: ta.Callable[[], object],
    ) -> object:
        key = (kind, obj)
        try:
            return self._inspection_cache[key]
        except KeyError:
            pass
        except TypeError:
            return factory()

        with self._lock:
            return self._cached_inspection(kind, obj, factory)

    def get_runtime_type_param(self, typ: TypeVarLikeType) -> object | None:
        return self._runtime_type_params_by_type.get(typ)

    def _to_runtime_annotation(
            self,
            typ: Type,
            *,
            type_alias_policy: TypeAliasAnnotationPolicy = 'expand',
    ) -> object:
        key = (typ, type_alias_policy)
        try:
            return self._annotation_cache[key]
        except KeyError:
            pass

        from .annotations import to_runtime_annotation

        annotation = to_runtime_annotation(
            typ,
            self._universe,
            type_var_resolver=self.get_runtime_type_param,
            type_alias_policy=type_alias_policy,
        )
        self._annotation_cache[key] = annotation
        return annotation

    def to_runtime_annotation(
            self,
            typ: Type,
            *,
            type_alias_policy: TypeAliasAnnotationPolicy = 'expand',
    ) -> object:
        key = (typ, type_alias_policy)
        try:
            return self._annotation_cache[key]
        except KeyError:
            pass

        with self._lock:
            return self._to_runtime_annotation(
                typ,
                type_alias_policy=type_alias_policy,
            )

    def _type_key(self, typ: Type) -> TypeKey:
        try:
            return self._type_key_cache[typ]
        except KeyError:
            pass

        key = type_key(typ)
        self._type_key_cache[typ] = key
        self._type_key_or_none_cache[typ] = key
        return key

    def type_key(self, typ: Type) -> TypeKey:
        try:
            return self._type_key_cache[typ]
        except KeyError:
            pass

        with self._lock:
            return self._type_key(typ)

    def _type_key_or_none(self, typ: Type) -> TypeKey | None:
        try:
            return self._type_key_or_none_cache[typ]
        except KeyError:
            pass

        key = type_key_or_none(typ)
        self._type_key_or_none_cache[typ] = key
        if key is not None:
            self._type_key_cache[typ] = key
        return key

    def type_key_or_none(self, typ: Type) -> TypeKey | None:
        try:
            return self._type_key_or_none_cache[typ]
        except KeyError:
            pass

        with self._lock:
            return self._type_key_or_none(typ)

    def _alpha_type_key(self, typ: Type) -> TypeKey:
        try:
            return self._alpha_type_key_cache[typ]
        except KeyError:
            pass

        key = alpha_type_key(typ)
        self._alpha_type_key_cache[typ] = key
        self._alpha_type_key_or_none_cache[typ] = key
        return key

    def alpha_type_key(self, typ: Type) -> TypeKey:
        try:
            return self._alpha_type_key_cache[typ]
        except KeyError:
            pass

        with self._lock:
            return self._alpha_type_key(typ)

    def _alpha_type_key_or_none(self, typ: Type) -> TypeKey | None:
        try:
            return self._alpha_type_key_or_none_cache[typ]
        except KeyError:
            pass

        key = alpha_type_key_or_none(typ)
        self._alpha_type_key_or_none_cache[typ] = key
        if key is not None:
            self._alpha_type_key_cache[typ] = key
        return key

    def alpha_type_key_or_none(self, typ: Type) -> TypeKey | None:
        try:
            return self._alpha_type_key_or_none_cache[typ]
        except KeyError:
            pass

        with self._lock:
            return self._alpha_type_key_or_none(typ)

    def _structural_type_key(self, typ: Type) -> TypeKey:
        try:
            return self._structural_type_key_cache[typ]
        except KeyError:
            pass

        key = structural_type_key(typ)
        self._structural_type_key_cache[typ] = key
        self._structural_type_key_or_none_cache[typ] = key
        return key

    def structural_type_key(self, typ: Type) -> TypeKey:
        try:
            return self._structural_type_key_cache[typ]
        except KeyError:
            pass

        with self._lock:
            return self._structural_type_key(typ)

    def _structural_type_key_or_none(self, typ: Type) -> TypeKey | None:
        try:
            return self._structural_type_key_or_none_cache[typ]
        except KeyError:
            pass

        key = structural_type_key_or_none(typ)
        self._structural_type_key_or_none_cache[typ] = key
        if key is not None:
            self._structural_type_key_cache[typ] = key
        return key

    def structural_type_key_or_none(self, typ: Type) -> TypeKey | None:
        try:
            return self._structural_type_key_or_none_cache[typ]
        except KeyError:
            pass

        with self._lock:
            return self._structural_type_key_or_none(typ)

    def _alpha_structural_type_key(self, typ: Type) -> TypeKey:
        try:
            return self._alpha_structural_type_key_cache[typ]
        except KeyError:
            pass

        key = alpha_structural_type_key(typ)
        self._alpha_structural_type_key_cache[typ] = key
        self._alpha_structural_type_key_or_none_cache[typ] = key
        return key

    def alpha_structural_type_key(self, typ: Type) -> TypeKey:
        try:
            return self._alpha_structural_type_key_cache[typ]
        except KeyError:
            pass

        with self._lock:
            return self._alpha_structural_type_key(typ)

    def _alpha_structural_type_key_or_none(self, typ: Type) -> TypeKey | None:
        try:
            return self._alpha_structural_type_key_or_none_cache[typ]
        except KeyError:
            pass

        key = alpha_structural_type_key_or_none(typ)
        self._alpha_structural_type_key_or_none_cache[typ] = key
        if key is not None:
            self._alpha_structural_type_key_cache[typ] = key
        return key

    def alpha_structural_type_key_or_none(self, typ: Type) -> TypeKey | None:
        try:
            return self._alpha_structural_type_key_or_none_cache[typ]
        except KeyError:
            pass

        with self._lock:
            return self._alpha_structural_type_key_or_none(typ)

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

        if _is_new_type(obj):
            return self._reflect_new_type(obj)

        origin = ta.get_origin(obj)
        args = ta.get_args(obj)

        if origin is not None:
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
                return make_union([self._reflect_type(arg) for arg in args])

            if isinstance(origin, ta.TypeAliasType):
                return self._reflect_type_alias(origin, args, is_subscripted=True)

            if origin is cabc.Callable:
                return self._reflect_callable(args)

            if origin is type:
                return self._reflect_type_type(args)

            if origin is tuple:
                return self._reflect_tuple(args)

            if _is_typed_dict_class(origin):
                return self._reflect_typed_dict(origin, args)

            return self._reflect_instance(origin, args)

        if _is_typed_dict_class(obj):
            return self._reflect_typed_dict(obj, ())  # type: ignore[arg-type]

        if isinstance(obj, type):
            return self._reflect_instance(obj, ())

        raise UnreflectableTypeError(f'Unsupported runtime type object: {obj!r}')

    def _reflect_forward_ref(self, obj: str | annotationlib.ForwardRef) -> Type:
        if isinstance(obj, str):
            name = obj
        else:
            name = obj.__forward_arg__

        for alias_obj in reversed(self._type_alias_stack):
            if name == alias_obj.__name__:
                return TypeAliasType(self._get_type_alias_symbol(alias_obj), [])
            if (alias_ref := self._reflect_type_alias_forward_ref(name, alias_obj)) is not None:
                return alias_ref

        if self._forward_ref_resolver is None:
            raise UnreflectableTypeError(f'Unsupported unresolved forward reference: {obj!r}')

        if name in self._resolving_forward_refs:
            raise UnreflectableTypeError(f'Recursive forward reference resolution: {name!r}')

        self._resolving_forward_refs.add(name)
        try:
            return self._reflect_type(self._forward_ref_resolver(name))
        finally:
            self._resolving_forward_refs.remove(name)

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

    def _reflect_type_alias_forward_ref_arg(
            self,
            name: str,
            parameter_names: ta.Mapping[str, object],
    ) -> Type:
        if not name.startswith('*'):
            return self._reflect_type(parameter_names[name])

        parameter = parameter_names[name[1:]]
        if not isinstance(parameter, ta.TypeVarTuple):
            raise KeyError(name)

        type_var_tuple = self._reflect_type(parameter)
        if not isinstance(type_var_tuple, TypeVarTupleType):
            raise KeyError(name)

        return TupleType(
            [UnpackType(type_var_tuple)],
            _make_tuple_fallback(self._universe),
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

        if obj in self._resolving_type_aliases:
            return TypeAliasType(alias, alias_args)

        self._resolving_type_aliases.add(obj)
        self._type_alias_stack.append(obj)
        try:
            target = self._reflect_type(obj.__value__)
        finally:
            self._type_alias_stack.pop()
            self._resolving_type_aliases.remove(obj)

        alias._target = target
        alias._is_recursive = None

        alias_type = TypeAliasType(alias, alias_args)
        if alias_type.is_recursive or self._contains_resolving_type_alias(target):
            alias._is_recursive = True
        return alias_type

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
        reflected_args.extend(self._reflect_type(arg) for arg in args[:prefix_len])

        variadic_start = prefix_len
        variadic_end = len(args) - suffix_len
        reflected_args.append(TupleType(
            [self._reflect_type(arg) for arg in args[variadic_start:variadic_end]],
            _make_tuple_fallback(self._universe),
        ))

        if suffix_len:
            reflected_args.extend(self._reflect_type(arg) for arg in args[-suffix_len:])

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
            return [self._reflect_type(arg) for arg in args]

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
        try:
            return self._runtime_aliases[obj]
        except KeyError:
            pass

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
        self._runtime_aliases[obj] = alias
        return alias

    def _contains_resolving_type_alias(self, typ: Type) -> bool:
        active_aliases = {
            self._runtime_aliases[obj]
            for obj in self._resolving_type_aliases
            if obj in self._runtime_aliases
        }
        if not active_aliases:
            return False
        return _contains_any_type_alias(typ, active_aliases, set())

    def _reflect_new_type(self, obj: object) -> Instance:
        info = self._universe.get_new_type_info(obj)
        info._new_type_supertype = self._reflect_type(obj.__supertype__)  # type: ignore[attr-defined]
        return Instance(info, [])

    def _reflect_annotated(self, args: tuple[object, ...]) -> AnnotatedType:
        if len(args) < 2:
            raise UnreflectableTypeError(f'Unsupported Annotated arguments: {args!r}')

        return AnnotatedType(self._reflect_type(args[0]), tuple(args[1:]))

    def _reflect_type_guard(self, args: tuple[object, ...]) -> TypeGuardedType:
        if len(args) != 1:
            raise UnreflectableTypeError(f'Unsupported TypeGuard arguments: {args!r}')

        return TypeGuardedType(self._reflect_type(args[0]))

    def _reflect_required(self, args: tuple[object, ...], *, required: bool) -> RequiredType:
        if len(args) != 1:
            raise UnreflectableTypeError(f'Unsupported Required arguments: {args!r}')

        return RequiredType(self._reflect_type(args[0]), required=required)

    def _reflect_read_only(self, args: tuple[object, ...]) -> ReadOnlyType:
        if len(args) != 1:
            raise UnreflectableTypeError(f'Unsupported ReadOnly arguments: {args!r}')

        return ReadOnlyType(self._reflect_type(args[0]))

    def _reflect_unpack(self, args: tuple[object, ...]) -> UnpackType:
        if len(args) != 1:
            raise UnreflectableTypeError(f'Unsupported Unpack arguments: {args!r}')

        return UnpackType(self._reflect_type(args[0]))

    def _reflect_typed_dict(self, origin: type, args: tuple[object, ...]) -> TypedDictType:
        parameters = getattr(origin, '__parameters__', ())
        if len(args) != len(parameters):
            raise UnreflectableTypeError(f'Unsupported TypedDict arguments for {origin!r}: {args!r}')

        replacements = {
            self._reflect_type_var_parameter(parameter): self._reflect_type(arg)
            for parameter, arg in zip(parameters, args)
        }

        required_keys = set(getattr(origin, '__required_keys__'))
        readonly_keys = set(getattr(origin, '__readonly_keys__', frozenset()))
        annotations = getattr(origin, '__annotations__')
        if not isinstance(annotations, dict):
            raise UnreflectableTypeError(f'Unsupported TypedDict annotations for {origin!r}: {annotations!r}')

        items: dict[str, Type] = {}
        for name, annotation in annotations.items():
            item = self._reflect_type(annotation)
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
        info = self._universe.get_type_info(origin)
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
            return [self._reflect_type(arg) for arg in args]

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
        if origin in self._prepared_infos:
            return
        self._prepared_infos.add(origin)

        parameters = getattr(origin, '__parameters__', ())
        if parameters and not info._type_vars:
            info._type_vars = [
                self._reflect_type_var_like_parameter(parameter)
                for parameter in parameters
            ]
            info._variances = [
                type_var._variance if isinstance(type_var, TypeVarType) else VarianceKind.IN
                for type_var in info.type_vars
            ]

        mro = getattr(origin, '__mro__', None)
        if mro is not None and info._mro == [info]:
            info._mro = [
                self._universe.get_type_info(cls)
                for cls in mro
                if isinstance(cls, type)
            ]

        if info._bases:
            return

        runtime_bases = self._get_runtime_bases(origin)
        info._bases = [
            self._reflect_runtime_base(base)
            for base in runtime_bases
        ]

    def _reflect_type_var_parameter(self, obj: object) -> TypeVarType:
        type_var = self._reflect_type(obj)
        if not isinstance(type_var, TypeVarType):
            raise UnreflectableTypeError(f'Unsupported generic parameter: {obj!r}')
        return type_var

    def _reflect_type_var_like_parameter(self, obj: object) -> TypeVarLikeType:
        type_var_like = self._reflect_type(obj)
        if not isinstance(type_var_like, TypeVarLikeType):
            raise UnreflectableTypeError(f'Unsupported generic parameter: {obj!r}')
        return type_var_like

    def _reflect_param_spec_parameter(self, obj: object) -> ParamSpecType:
        param_spec = self._reflect_type(obj)
        if not isinstance(param_spec, ParamSpecType):
            raise UnreflectableTypeError(f'Unsupported ParamSpec parameter: {obj!r}')
        return param_spec

    def _get_runtime_bases(self, origin: type) -> tuple[object, ...]:
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

    def _reflect_runtime_base(self, obj: object) -> Instance:
        base = self._reflect_type(obj)
        if not isinstance(base, Instance):
            raise UnreflectableTypeError(f'Unsupported runtime base: {obj!r}')
        return base

    def _reflect_tuple(self, args: tuple[object, ...]) -> Type:
        info = self._universe.get_type_info(tuple)

        if len(args) == 2 and args[1] is Ellipsis:
            return Instance(info, [self._reflect_type(args[0])])

        fallback = Instance(info, [_make_any()])
        return TupleType([self._reflect_type(arg) for arg in args], fallback)

    def _reflect_single_arg_wrapper(self, origin: object, args: tuple[object, ...]) -> Type:
        if len(args) != 1:
            raise UnreflectableTypeError(f'Unsupported wrapper arguments for {origin!r}: {args!r}')

        return self._reflect_type(args[0])

    def _reflect_type_type(self, args: tuple[object, ...]) -> TypeType:
        if len(args) != 1:
            raise UnreflectableTypeError(f'Unsupported type arguments: {args!r}')

        return TypeType(self._reflect_type(args[0]))

    def _reflect_callable(self, args: tuple[object, ...]) -> CallableType:
        fallback = Instance(
            self._universe.get_type_info(cabc.Callable),  # type: ignore[arg-type]
            [_make_any()],
        )

        if len(args) != 2:
            raise UnreflectableTypeError(f'Unsupported Callable arguments: {args!r}')

        arg_spec, ret_type = args
        if arg_spec is Ellipsis:
            return CallableType(
                [],
                [],
                [],
                self._reflect_type(ret_type),
                fallback,
                is_ellipsis_args=True,
            )

        if isinstance(arg_spec, ta.ParamSpec):
            param_spec = self._reflect_param_spec_parameter(arg_spec)
            return CallableType(
                [param_spec, param_spec],
                [ArgKind.STAR, ArgKind.STAR2],
                [None, None],
                self._reflect_type(ret_type),
                fallback,
                variables=[param_spec],
            )

        if ta.get_origin(arg_spec) is ta.Concatenate:
            concatenate_args = ta.get_args(arg_spec)
            if len(concatenate_args) < 2 or not isinstance(concatenate_args[-1], ta.ParamSpec):
                raise UnreflectableTypeError(f'Unsupported Concatenate argument specification: {arg_spec!r}')

            param_spec = self._reflect_param_spec_parameter(concatenate_args[-1])
            prefix_types = [self._reflect_type(arg) for arg in concatenate_args[:-1]]
            return CallableType(
                [*prefix_types, param_spec, param_spec],
                [*[ArgKind.POS for _ in prefix_types], ArgKind.STAR, ArgKind.STAR2],
                [*[None for _ in prefix_types], None, None],
                self._reflect_type(ret_type),
                fallback,
                variables=[param_spec],
            )

        if not isinstance(arg_spec, list):
            raise UnreflectableTypeError(f'Unsupported Callable argument specification: {arg_spec!r}')

        arg_types = [self._reflect_type(arg) for arg in arg_spec]
        return CallableType(
            arg_types,
            [ArgKind.POS for _ in arg_types],
            [None for _ in arg_types],
            self._reflect_type(ret_type),
            fallback,
        )

    def _reflect_literal(self, args: tuple[object, ...]) -> Type:
        items = [self._reflect_literal_value(arg) for arg in args]
        if len(items) == 1:
            return items[0]
        return make_union(items)

    def _reflect_literal_value(self, obj: object) -> LiteralType:
        if isinstance(obj, enum.Enum):
            fallback = Instance(self._universe.get_type_info(obj.__class__), [])
            return LiteralType(obj.name, fallback)

        if not _is_literal_value(obj):
            raise UnreflectableTypeError(f'Unsupported literal value: {obj!r}')

        fallback = Instance(self._universe.get_type_info(type(obj)), [])
        return LiteralType(ta.cast(LiteralValue, obj), fallback)

    def _reflect_type_var(self, obj: ta.TypeVar) -> TypeVarType:
        if obj.__covariant__:
            variance = VarianceKind.CO
        elif obj.__contravariant__:
            variance = VarianceKind.CONTRA
        else:
            variance = VarianceKind.IN

        bound = obj.__bound__
        if bound is None:
            upper_bound: Type = Instance(self._universe.get_type_info(object), [])
        else:
            upper_bound = self._reflect_type(bound)

        default_obj = getattr(obj, '__default__', ta.NoDefault)
        if default_obj is ta.NoDefault:
            default: Type = _make_any()
        else:
            default = self._reflect_type(default_obj)

        type_var = TypeVarType(
            obj.__name__,
            obj.__name__,
            TypeVarId(self._next_type_var_id, namespace=self._type_var_namespace),
            [self._reflect_type(value) for value in obj.__constraints__],
            upper_bound,
            default,
            variance,
        )
        self._next_type_var_id += 1
        self._runtime_type_params_by_type[type_var] = obj
        return type_var

    def _reflect_param_spec(self, obj: ta.ParamSpec) -> ParamSpecType:
        upper_bound = Instance(self._universe.get_type_info(object), [])

        default_obj = getattr(obj, '__default__', ta.NoDefault)
        if default_obj is ta.NoDefault:
            default: Type = _make_any()
        else:
            default = self._reflect_type(default_obj)

        param_spec = ParamSpecType(
            obj.__name__,
            obj.__name__,
            TypeVarId(self._next_type_var_id, namespace=self._type_var_namespace),
            upper_bound,
            default,
        )
        self._next_type_var_id += 1
        self._runtime_type_params_by_type[param_spec] = obj
        return param_spec

    def _reflect_type_var_tuple(self, obj: ta.TypeVarTuple) -> TypeVarTupleType:
        upper_bound = Instance(self._universe.get_type_info(object), [])

        default_obj = getattr(obj, '__default__', ta.NoDefault)
        if default_obj is ta.NoDefault:
            default: Type = _make_any()
        else:
            default = self._reflect_type(default_obj)

        tuple_fallback = Instance(self._universe.get_type_info(tuple), [_make_any()])
        type_var_tuple = TypeVarTupleType(
            obj.__name__,
            obj.__name__,
            TypeVarId(self._next_type_var_id, namespace=self._type_var_namespace),
            upper_bound,
            default,
            tuple_fallback,
        )
        self._next_type_var_id += 1
        self._runtime_type_params_by_type[type_var_tuple] = obj
        return type_var_tuple


DEFAULT_REFLECTOR = RuntimeTypeReflector()


def make_runtime_reflector(
        *,
        dynamic_type_name_suffix: DynamicTypeNameSuffix = 'id',
        forward_ref_resolver: ForwardRefResolver | None = None,
) -> RuntimeTypeReflector:
    return RuntimeTypeReflector(
        RuntimeTypeUniverse(dynamic_type_name_suffix=dynamic_type_name_suffix),
        forward_ref_resolver=forward_ref_resolver,
    )


def reflect_type(obj: object) -> Type:
    return DEFAULT_REFLECTOR.reflect_type(obj)
