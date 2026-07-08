# ruff: noqa: A002 SLF001 UP007
"""
Unlike in mypy these types are part of the public api - internal code *should* access private fields, but for external
code it is hidden behind properties.
"""
import enum
import typing as ta

from ..errors import ReflectionValueError
from .symbols import ArgKind
from .symbols import TypeAlias
from .symbols import TypeInfo
from .symbols import VarianceKind


if ta.TYPE_CHECKING:
    from .typekeys import StandardTypeKeyPolicy
    from .typekeys import TypeKey
    from .typevisitor import TypeVisitor


T = ta.TypeVar('T')

LiteralValue: ta.TypeAlias = ta.Union[
    bool,
    int,
    float,
    str,
    bytes,
    None,
]

_LITERAL_VALUE_TYPES: ta.Final[tuple[type[LiteralValue], ...]] = (
    bool,
    int,
    float,
    str,
    bytes,
    type(None),
)


##


def is_literal_value(value: object) -> bool:
    return value is None or type(value) in _LITERAL_VALUE_TYPES


##


class Type:
    """Strict single inheritance hierarchy. All non-final classes are considered abstract."""

    __slots__ = (
        '_type_key_cache',
    )

    def __init__(self) -> None:
        super().__init__()

        self._type_key_cache: dict[StandardTypeKeyPolicy, TypeKey | None] = {}

    def __str__(self) -> str:
        from .strconv import type_str

        return type_str(self)

    def __repr__(self) -> str:
        from .strconv import type_str

        return type_str(self)

    #

    def accept(self, visitor: TypeVisitor[T]) -> T:
        raise NotImplementedError

    #

    @property
    def runtime_object(self) -> object | None:
        return None

    #

    def type_key_or_none(self, policy: StandardTypeKeyPolicy = 'default') -> TypeKey | None:
        try:
            return self._type_key_cache[policy]
        except KeyError:
            pass

        from .typekeys import type_key_or_none

        tk = type_key_or_none(self, policy)
        self._type_key_cache[policy] = tk
        return tk

    def type_key(self, policy: StandardTypeKeyPolicy = 'default') -> TypeKey:
        key = self.type_key_or_none(policy)

        if key is None:
            from .typekeys import make_type_key_not_implemented_exception

            raise make_type_key_not_implemented_exception(self, policy)

        return key


@ta.final
class TypeAliasType(Type):
    __slots__ = (
        '_alias',
        '_args',
    )

    def __init__(
            self,
            alias: TypeAlias | None,
            args: ta.Sequence[Type],
    ) -> None:
        super().__init__()

        self._alias = alias
        self._args = tuple(args)

    @property
    def alias(self) -> TypeAlias | None:
        return self._alias

    @property
    def args(self) -> tuple[Type, ...]:
        return self._args

    @property
    def is_recursive(self) -> bool:
        if self._alias is None:
            return False

        if self._alias._is_recursive is None:
            from .typeops import is_recursive_alias

            self._alias._is_recursive = is_recursive_alias(self._alias)

        return self._alias._is_recursive  # noqa

    def accept(self, visitor: TypeVisitor[T]) -> T:
        return visitor.visit_type_alias_type(self)


@ta.final
class TypeGuardedType(Type):
    __slots__ = (
        '_type_guard',
    )

    def __init__(self, type_guard: Type) -> None:
        super().__init__()

        self._type_guard = type_guard

    @property
    def type_guard(self) -> Type:
        return self._type_guard

    def accept(self, visitor: TypeVisitor[T]) -> T:
        return visitor.visit_type_guarded_type(self)


@ta.final
class AnnotatedType(Type):
    __slots__ = (
        '_item',
        '_metadata',
    )

    def __init__(
            self,
            item: Type,
            metadata: tuple[object, ...],
    ) -> None:
        super().__init__()

        if not metadata:
            raise ReflectionValueError('AnnotatedType metadata must be non-empty')

        self._item = item
        self._metadata = metadata

    @property
    def item(self) -> Type:
        return self._item

    @property
    def metadata(self) -> tuple[object, ...]:
        return self._metadata

    def accept(self, visitor: TypeVisitor[T]) -> T:
        return visitor.visit_annotated_type(self)


@ta.final
class RequiredType(Type):
    __slots__ = (
        '_item',
        '_required',
    )

    def __init__(
            self,
            item: Type,
            *,
            required: bool = True,
    ) -> None:
        super().__init__()

        self._item = item
        self._required = required

    @property
    def item(self) -> Type:
        return self._item

    @property
    def required(self) -> bool:
        return self._required

    def accept(self, visitor: TypeVisitor[T]) -> T:
        return visitor.visit_required_type(self)


@ta.final
class ReadOnlyType(Type):
    __slots__ = (
        '_item',
    )

    def __init__(self, item: Type) -> None:
        super().__init__()

        self._item = item

    @property
    def item(self) -> Type:
        return self._item

    def accept(self, visitor: TypeVisitor[T]) -> T:
        return visitor.visit_read_only_type(self)


class ProperType(Type):
    __slots__ = ()


class TypeVarId:
    __slots__ = (
        '_raw_id',
        '_meta_level',
        '_namespace',
    )

    def __init__(
            self,
            raw_id: int,
            meta_level: int = 0,
            namespace: str = '',
    ) -> None:
        super().__init__()

        self._raw_id = raw_id
        self._meta_level = meta_level
        self._namespace = namespace

    @property
    def raw_id(self) -> int:
        return self._raw_id

    @property
    def meta_level(self) -> int:
        return self._meta_level

    @property
    def namespace(self) -> str:
        return self._namespace


class TypeVarLikeType(ProperType):
    __slots__ = (
        '_name',
        '_fullname',
        '_id',
        '_upper_bound',
        '_default',
        '_runtime_object',
    )

    def __init__(
            self,
            name: str,
            fullname: str,
            id: TypeVarId,
            upper_bound: Type,
            default: Type,
            *,
            runtime_object: object | None = None,
    ) -> None:
        super().__init__()

        self._name = name
        self._fullname = fullname
        self._id = id
        self._upper_bound = upper_bound
        self._default = default
        self._runtime_object = runtime_object

    @property
    def name(self) -> str:
        return self._name

    @property
    def fullname(self) -> str:
        return self._fullname

    @property
    def id(self) -> TypeVarId:
        return self._id

    @property
    def upper_bound(self) -> Type:
        return self._upper_bound

    @property
    def default(self) -> Type:
        return self._default

    @property
    def runtime_object(self) -> object | None:
        return self._runtime_object


@ta.final
class TypeVarType(TypeVarLikeType):
    __slots__ = (
        '_values',
        '_variance',
    )

    def __init__(
            self,
            name: str,
            fullname: str,
            id: TypeVarId,
            values: ta.Sequence[Type],
            upper_bound: Type,
            default: Type,
            variance: VarianceKind = VarianceKind.IN,
            *,
            runtime_object: object | None = None,
    ) -> None:
        super().__init__(
            name,
            fullname,
            id,
            upper_bound,
            default,
            runtime_object=runtime_object,
        )

        self._values = tuple(values)
        self._variance = variance

    @property
    def values(self) -> tuple[Type, ...]:
        return self._values

    @property
    def variance(self) -> VarianceKind:
        return self._variance

    def accept(self, visitor: TypeVisitor[T]) -> T:
        return visitor.visit_type_var(self)


@ta.final
class ParamSpecType(TypeVarLikeType):
    __slots__ = (
        '_flavor',
    )

    def __init__(
            self,
            name: str,
            fullname: str,
            id: TypeVarId,
            upper_bound: Type,
            default: Type,
            flavor: int = 0,
            *,
            runtime_object: object | None = None,
    ) -> None:
        super().__init__(
            name,
            fullname,
            id,
            upper_bound,
            default,
            runtime_object=runtime_object,
        )

        self._flavor = flavor

    @property
    def flavor(self) -> int:
        return self._flavor

    def accept(self, visitor: TypeVisitor[T]) -> T:
        return visitor.visit_param_spec(self)


@ta.final
class TypeVarTupleType(TypeVarLikeType):
    __slots__ = (
        '_tuple_fallback',
    )

    def __init__(
            self,
            name: str,
            fullname: str,
            id: TypeVarId,
            upper_bound: Type,
            default: Type,
            tuple_fallback: Type,
            *,
            runtime_object: object | None = None,
    ) -> None:
        super().__init__(
            name,
            fullname,
            id,
            upper_bound,
            default,
            runtime_object=runtime_object,
        )

        self._tuple_fallback = tuple_fallback

    @property
    def tuple_fallback(self) -> Type:
        return self._tuple_fallback

    def accept(self, visitor: TypeVisitor[T]) -> T:
        return visitor.visit_type_var_tuple(self)


@ta.final
class UnboundType(ProperType):
    __slots__ = (
        '_name',
        '_args',
        '_runtime_object',
    )

    def __init__(
            self,
            name: str,
            args: ta.Sequence[Type] | None = None,
            *,
            runtime_object: object | None = None,
    ) -> None:
        super().__init__()

        self._name = name
        self._args = () if args is None else tuple(args)

        # Unlike mypy's purely name-based UnboundType, we may retain a hard ref to the runtime type-form object the name
        # came from (typically an `annotationlib.ForwardRef`) - this is what makes a specific unresolved forward
        # reference `is`-distinguishable from an identically-named one elsewhere. Mirrors `TypeAlias.runtime_object`.
        self._runtime_object = runtime_object

    @property
    def name(self) -> str:
        return self._name

    @property
    def args(self) -> tuple[Type, ...]:
        return self._args

    @property
    def runtime_object(self) -> object | None:
        return self._runtime_object

    def accept(self, visitor: TypeVisitor[T]) -> T:
        return visitor.visit_unbound_type(self)


@ta.final
class CallableArgument(ProperType):
    __slots__ = (
        '_typ',
        '_name',
        '_constructor',
    )

    def __init__(
            self,
            typ: Type,
            name: str | None,
            constructor: str | None = None,
    ) -> None:
        super().__init__()

        self._typ = typ
        self._name = name
        self._constructor = constructor

    @property
    def typ(self) -> Type:
        return self._typ

    @property
    def name(self) -> str | None:
        return self._name

    @property
    def constructor(self) -> str | None:
        return self._constructor

    def accept(self, visitor: TypeVisitor[T]) -> T:
        return visitor.visit_callable_argument(self)


@ta.final
class TypeList(ProperType):
    __slots__ = (
        '_items',
    )

    def __init__(self, items: ta.Sequence[Type]) -> None:
        super().__init__()

        self._items = tuple(items)

    @property
    def items(self) -> tuple[Type, ...]:
        return self._items

    def accept(self, visitor: TypeVisitor[T]) -> T:
        return visitor.visit_type_list(self)


@ta.final
class UnpackType(ProperType):
    __slots__ = (
        '_type',
    )

    def __init__(self, typ: Type) -> None:
        super().__init__()

        self._type = typ

    @property
    def type(self) -> Type:
        return self._type

    def accept(self, visitor: TypeVisitor[T]) -> T:
        return visitor.visit_unpack_type(self)


class TypeOfAny(enum.Enum):
    UNANNOTATED = 1
    EXPLICIT = 2
    FROM_UNIMPORTED_TYPE = 3
    FROM_OMITTED_GENERICS = 4
    FROM_ERROR = 5
    SPECIAL_FORM = 6
    FROM_ANOTHER_ANY = 7
    IMPLEMENTATION_ARTIFACT = 8
    SUGGESTION_ENGINE = 9


_ANY_RUNTIME_TYPE: ta.Any = ta.Any


@ta.final
class AnyType(ProperType):
    __slots__ = (
        '_type_of_any',
    )

    def __init__(self, type_of_any: TypeOfAny) -> None:
        super().__init__()

        self._type_of_any = type_of_any

    @property
    def type_of_any(self) -> TypeOfAny:
        return self._type_of_any

    @property
    def runtime_object(self) -> object | None:
        return _ANY_RUNTIME_TYPE

    def accept(self, visitor: TypeVisitor[T]) -> T:
        return visitor.visit_any(self)


_ANY_TYPES: ta.Final[dict[TypeOfAny, AnyType]] = {
    toa: AnyType(toa)
    for toa in TypeOfAny
}


def any_type(type_of_any: TypeOfAny) -> AnyType:
    return _ANY_TYPES[type_of_any]


@ta.final
class UninhabitedType(ProperType):
    __slots__ = ()

    def accept(self, visitor: TypeVisitor[T]) -> T:
        return visitor.visit_uninhabited_type(self)


_UNINHABITED_TYPE: ta.Final = UninhabitedType()


def uninhabited_type() -> UninhabitedType:
    return _UNINHABITED_TYPE


_NONE_RUNTIME_TYPE: ta.Final = type(None)


@ta.final
class NoneType(ProperType):
    __slots__ = ()

    @property
    def runtime_object(self) -> object | None:
        return _NONE_RUNTIME_TYPE

    def accept(self, visitor: TypeVisitor[T]) -> T:
        return visitor.visit_none_type(self)


_NONE_TYPE: ta.Final = NoneType()


def none_type() -> NoneType:
    return _NONE_TYPE


@ta.final
class ErasedType(ProperType):
    __slots__ = ()

    def accept(self, visitor: TypeVisitor[T]) -> T:
        return visitor.visit_erased_type(self)


_ERASED_TYPE: ta.Final = ErasedType()


def erased_type() -> ErasedType:
    return _ERASED_TYPE


@ta.final
class DeletedType(ProperType):
    __slots__ = (
        '_source',
    )

    def __init__(self, source: str | None = None) -> None:
        super().__init__()

        self._source = source

    @property
    def source(self) -> str | None:
        return self._source

    def accept(self, visitor: TypeVisitor[T]) -> T:
        return visitor.visit_deleted_type(self)


class ExtraAttrs:
    __slots__ = (
        '_attrs',
    )

    def __init__(self, attrs: ta.Mapping[str, Type]) -> None:
        super().__init__()

        self._attrs = attrs

    @property
    def attrs(self) -> ta.Mapping[str, Type]:
        return self._attrs


@ta.final
class Instance(ProperType):
    __slots__ = (
        '_type',
        '_args',
        '_last_known_value',
        '_extra_attrs',
    )

    def __init__(
            self,
            typ: TypeInfo,
            args: ta.Sequence[Type],
            *,
            last_known_value: LiteralType | None = None,
            extra_attrs: ExtraAttrs | None = None,
    ) -> None:
        super().__init__()

        self._type = typ
        self._args = tuple(args)
        self._last_known_value = last_known_value
        self._extra_attrs = extra_attrs

    @property
    def type(self) -> TypeInfo:
        return self._type

    @property
    def args(self) -> tuple[Type, ...]:
        return self._args

    @property
    def last_known_value(self) -> LiteralType | None:
        return self._last_known_value

    @property
    def extra_attrs(self) -> ExtraAttrs | None:
        return self._extra_attrs

    @property
    def runtime_object(self) -> object | None:
        return self._type.runtime_object

    def accept(self, visitor: TypeVisitor[T]) -> T:
        return visitor.visit_instance(self)


class FunctionLike(ProperType):
    __slots__ = (
        '_fallback',
    )

    def __init__(self, fallback: Instance) -> None:
        super().__init__()

        self._fallback = fallback

    @property
    def fallback(self) -> Instance:
        return self._fallback


class FormalArgument:
    __slots__ = (
        '_name',
        '_pos',
        '_typ',
        '_required',
    )

    def __init__(
            self,
            name: str | None,
            pos: int | None,
            typ: Type,
            required: bool,
    ) -> None:
        super().__init__()

        self._name = name
        self._pos = pos
        self._typ = typ
        self._required = required

    @property
    def name(self) -> str | None:
        return self._name

    @property
    def pos(self) -> int | None:
        return self._pos

    @property
    def typ(self) -> Type:
        return self._typ

    @property
    def required(self) -> bool:
        return self._required


@ta.final
class Parameters(ProperType):
    __slots__ = (
        '_arg_types',
        '_arg_kinds',
        '_arg_names',
    )

    def __init__(
            self,
            arg_types: ta.Sequence[Type],
            arg_kinds: ta.Sequence[ArgKind],
            arg_names: ta.Sequence[str | None],
    ) -> None:
        super().__init__()

        self._arg_types = tuple(arg_types)
        self._arg_kinds = tuple(arg_kinds)
        self._arg_names = tuple(arg_names)

    @property
    def arg_types(self) -> tuple[Type, ...]:
        return self._arg_types

    @property
    def arg_kinds(self) -> tuple[ArgKind, ...]:
        return self._arg_kinds

    @property
    def arg_names(self) -> tuple[str | None, ...]:
        return self._arg_names

    def accept(self, visitor: TypeVisitor[T]) -> T:
        return visitor.visit_parameters(self)


@ta.final
class CallableType(FunctionLike):
    __slots__ = (
        '_arg_types',
        '_arg_kinds',
        '_arg_names',
        '_ret_type',
        '_variables',
        '_is_ellipsis_args',
    )

    def __init__(
            self,
            arg_types: ta.Sequence[Type],
            arg_kinds: ta.Sequence[ArgKind],
            arg_names: ta.Sequence[str | None],
            ret_type: Type,
            fallback: Instance,
            *,
            variables: ta.Sequence[TypeVarLikeType] | None = None,
            is_ellipsis_args: bool = False,
    ) -> None:
        super().__init__(fallback)

        self._arg_types = tuple(arg_types)
        self._arg_kinds = tuple(arg_kinds)
        self._arg_names = tuple(arg_names)
        self._ret_type = ret_type
        self._variables = () if variables is None else tuple(variables)
        self._is_ellipsis_args = is_ellipsis_args

    @property
    def arg_types(self) -> tuple[Type, ...]:
        return self._arg_types

    @property
    def arg_kinds(self) -> tuple[ArgKind, ...]:
        return self._arg_kinds

    @property
    def arg_names(self) -> tuple[str | None, ...]:
        return self._arg_names

    @property
    def ret_type(self) -> Type:
        return self._ret_type

    @property
    def variables(self) -> tuple[TypeVarLikeType, ...]:
        return self._variables

    @property
    def is_ellipsis_args(self) -> bool:
        return self._is_ellipsis_args

    def accept(self, visitor: TypeVisitor[T]) -> T:
        return visitor.visit_callable_type(self)


@ta.final
class Overloaded(FunctionLike):
    __slots__ = (
        '_items',
    )

    def __init__(self, items: ta.Sequence[CallableType]) -> None:
        if not items:
            raise ReflectionValueError('Overloaded requires at least one item')

        super().__init__(items[0].fallback)

        self._items = tuple(items)

    @property
    def items(self) -> tuple[CallableType, ...]:
        return self._items

    def accept(self, visitor: TypeVisitor[T]) -> T:
        return visitor.visit_overloaded(self)


@ta.final
class TupleType(ProperType):
    __slots__ = (
        '_items',
        '_partial_fallback',
    )

    def __init__(
            self,
            items: ta.Sequence[Type],
            partial_fallback: Instance,
    ) -> None:
        super().__init__()

        self._items = tuple(items)
        self._partial_fallback = partial_fallback

    @property
    def items(self) -> tuple[Type, ...]:
        return self._items

    @property
    def partial_fallback(self) -> Instance:
        return self._partial_fallback

    def accept(self, visitor: TypeVisitor[T]) -> T:
        return visitor.visit_tuple_type(self)


@ta.final
class TypedDictType(ProperType):
    __slots__ = (
        '_items',
        '_required_keys',
        '_readonly_keys',
        '_fallback',
    )

    def __init__(
            self,
            items: ta.Mapping[str, Type],
            required_keys: ta.AbstractSet[str],
            readonly_keys: ta.AbstractSet[str],
            fallback: Instance,
    ) -> None:
        super().__init__()

        self._items = items
        self._required_keys = frozenset(required_keys)
        self._readonly_keys = frozenset(readonly_keys)
        self._fallback = fallback

    @property
    def items(self) -> ta.Mapping[str, Type]:
        return self._items

    @property
    def required_keys(self) -> frozenset[str]:
        return self._required_keys

    @property
    def readonly_keys(self) -> frozenset[str]:
        return self._readonly_keys

    @property
    def fallback(self) -> Instance:
        return self._fallback

    def accept(self, visitor: TypeVisitor[T]) -> T:
        return visitor.visit_typeddict_type(self)


@ta.final
class RawExpressionType(ProperType):
    __slots__ = (
        '_literal_value',
        '_base_type_name',
    )

    def __init__(
            self,
            literal_value: LiteralValue | None,
            base_type_name: str,
    ) -> None:
        super().__init__()

        self._literal_value = literal_value
        self._base_type_name = base_type_name

    @property
    def literal_value(self) -> LiteralValue | None:
        return self._literal_value

    @property
    def base_type_name(self) -> str:
        return self._base_type_name

    def accept(self, visitor: TypeVisitor[T]) -> T:
        return visitor.visit_raw_expression_type(self)


@ta.final
class LiteralType(ProperType):
    __slots__ = (
        '_value',
        '_fallback',
    )

    def __init__(
            self,
            value: LiteralValue,
            fallback: Instance,
    ) -> None:
        super().__init__()

        self._value = value
        self._fallback = fallback

    @property
    def value(self) -> LiteralValue:
        return self._value

    @property
    def fallback(self) -> Instance:
        return self._fallback

    def accept(self, visitor: TypeVisitor[T]) -> T:
        return visitor.visit_literal_type(self)


@ta.final
class UnionType(ProperType):
    __slots__ = (
        '_items',
        '_is_optional',
        '_strip_optional',
    )

    def __init__(self, items: ta.Sequence[Type]) -> None:
        super().__init__()

        from .typeops import flatten_nested_unions

        self._items = tuple(flatten_nested_unions(items, handle_type_alias_type=False))
        if len(self._items) < 1:
            raise ReflectionValueError('Union requires at least one item')

        self._is_optional = any(isinstance(item, NoneType) for item in self._items)
        self._strip_optional: list[Type | None] = [None]  # freethreading hack

    @property
    def items(self) -> tuple[Type, ...]:
        return self._items

    @property
    def is_optional(self) -> bool:
        return self._is_optional

    def strip_optional(self) -> Type:
        if not self._is_optional:
            return self
        if (ret := self._strip_optional[0]) is not None:
            return ret

        from .typeops import make_union

        ret = make_union([
            item
            for item in self._items
            if not isinstance(item, NoneType)
        ])
        self._strip_optional[0] = ret
        return ret

    def accept(self, visitor: TypeVisitor[T]) -> T:
        return visitor.visit_union_type(self)


@ta.final
class PartialType(ProperType):
    __slots__ = (
        '_type',
        '_var',
        '_value_type',
    )

    def __init__(
            self,
            typ: TypeInfo | None,
            var: object | None,
            value_type: Type | None = None,
    ) -> None:
        super().__init__()

        self._type = typ
        self._var = var
        self._value_type = value_type

    @property
    def type(self) -> TypeInfo | None:
        return self._type

    @property
    def var(self) -> object | None:
        return self._var

    @property
    def value_type(self) -> Type | None:
        return self._value_type

    def accept(self, visitor: TypeVisitor[T]) -> T:
        return visitor.visit_partial_type(self)


@ta.final
class EllipsisType(ProperType):
    __slots__ = ()

    def accept(self, visitor: TypeVisitor[T]) -> T:
        return visitor.visit_ellipsis_type(self)


_ELLIPSIS_TYPE: ta.Final = EllipsisType()


def ellipsis_type() -> EllipsisType:
    return _ELLIPSIS_TYPE


@ta.final
class TypeType(ProperType):
    __slots__ = (
        '_item',
    )

    def __init__(self, item: Type) -> None:
        super().__init__()

        self._item = item

    @property
    def item(self) -> Type:
        return self._item

    def accept(self, visitor: TypeVisitor[T]) -> T:
        return visitor.visit_type_type(self)


@ta.final
class PlaceholderType(ProperType):
    __slots__ = (
        '_fullname',
        '_args',
    )

    def __init__(
            self,
            fullname: str,
            args: ta.Sequence[Type] | None = None,
    ) -> None:
        super().__init__()

        self._fullname = fullname
        self._args = () if args is None else tuple(args)

    @property
    def fullname(self) -> str:
        return self._fullname

    @property
    def args(self) -> tuple[Type, ...]:
        return self._args

    def accept(self, visitor: TypeVisitor[T]) -> T:
        return visitor.visit_placeholder_type(self)


@ta.final
class _TestingUnknownType(Type):
    """Exists for testing."""

    __slots__ = ()
