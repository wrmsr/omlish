# ruff: noqa: SLF001
import abc
import enum
import typing as ta

from ..errors import ReflectionTypeError
from ..errors import ReflectionValueError
from .types import AnnotatedType
from .types import AnyType
from .types import CallableArgument
from .types import CallableType
from .types import DeletedType
from .types import EllipsisType
from .types import ErasedType
from .types import FunctionLike
from .types import Instance
from .types import LiteralType
from .types import NoneType
from .types import Overloaded
from .types import Parameters
from .types import ParamSpecType
from .types import PartialType
from .types import PlaceholderType
from .types import ProperType
from .types import RawExpressionType
from .types import ReadOnlyType
from .types import RequiredType
from .types import TupleType
from .types import Type
from .types import TypeAliasType
from .types import TypedDictType
from .types import TypeGuardedType
from .types import TypeList
from .types import TypeType
from .types import TypeVarLikeType
from .types import TypeVarTupleType
from .types import TypeVarType
from .types import UnboundType
from .types import UninhabitedType
from .types import UnionType
from .types import UnpackType


try:
    from mypy_extensions import mypyc_attr
    from mypy_extensions import trait
except ImportError:
    from ._mypycshim import mypyc_attr
    from ._mypycshim import trait


T = ta.TypeVar('T')


##


@trait
@mypyc_attr(allow_interpreted_subclasses=True)
class TypeVisitor(ta.Generic[T]):
    @abc.abstractmethod
    def visit_type_alias_type(self, typ: TypeAliasType) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_type_guarded_type(self, typ: TypeGuardedType) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_annotated_type(self, typ: AnnotatedType) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_required_type(self, typ: RequiredType) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_read_only_type(self, typ: ReadOnlyType) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_type_var(self, typ: TypeVarType) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_param_spec(self, typ: ParamSpecType) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_type_var_tuple(self, typ: TypeVarTupleType) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_unbound_type(self, typ: UnboundType) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_callable_argument(self, typ: CallableArgument) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_type_list(self, typ: TypeList) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_unpack_type(self, typ: UnpackType) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_any(self, typ: AnyType) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_uninhabited_type(self, typ: UninhabitedType) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_none_type(self, typ: NoneType) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_erased_type(self, typ: ErasedType) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_deleted_type(self, typ: DeletedType) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_instance(self, typ: Instance) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_parameters(self, typ: Parameters) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_callable_type(self, typ: CallableType) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_overloaded(self, typ: Overloaded) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_tuple_type(self, typ: TupleType) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_typeddict_type(self, typ: TypedDictType) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_raw_expression_type(self, typ: RawExpressionType) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_literal_type(self, typ: LiteralType) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_union_type(self, typ: UnionType) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_partial_type(self, typ: PartialType) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_ellipsis_type(self, typ: EllipsisType) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_type_type(self, typ: TypeType) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_placeholder_type(self, typ: PlaceholderType) -> T:
        raise NotImplementedError


#


@trait
@mypyc_attr(allow_interpreted_subclasses=True)
class DefaultTypeVisitor(TypeVisitor[T]):
    @abc.abstractmethod
    def visit_type(self, typ: Type) -> T:
        raise NotImplementedError

    @ta.override
    def visit_type_alias_type(self, typ: TypeAliasType) -> T:
        return self.visit_type(typ)

    @ta.override
    def visit_type_guarded_type(self, typ: TypeGuardedType) -> T:
        return self.visit_type(typ)

    @ta.override
    def visit_annotated_type(self, typ: AnnotatedType) -> T:
        return self.visit_type(typ)

    @ta.override
    def visit_required_type(self, typ: RequiredType) -> T:
        return self.visit_type(typ)

    @ta.override
    def visit_read_only_type(self, typ: ReadOnlyType) -> T:
        return self.visit_type(typ)

    def visit_proper_type(self, typ: ProperType) -> T:
        return self.visit_type(typ)

    def visit_type_var_like_type(self, typ: TypeVarLikeType) -> T:
        return self.visit_proper_type(typ)

    @ta.override
    def visit_type_var(self, typ: TypeVarType) -> T:
        return self.visit_type_var_like_type(typ)

    @ta.override
    def visit_param_spec(self, typ: ParamSpecType) -> T:
        return self.visit_type_var_like_type(typ)

    @ta.override
    def visit_type_var_tuple(self, typ: TypeVarTupleType) -> T:
        return self.visit_type_var_like_type(typ)

    @ta.override
    def visit_unbound_type(self, typ: UnboundType) -> T:
        return self.visit_proper_type(typ)

    @ta.override
    def visit_callable_argument(self, typ: CallableArgument) -> T:
        return self.visit_proper_type(typ)

    @ta.override
    def visit_type_list(self, typ: TypeList) -> T:
        return self.visit_proper_type(typ)

    @ta.override
    def visit_unpack_type(self, typ: UnpackType) -> T:
        return self.visit_proper_type(typ)

    @ta.override
    def visit_any(self, typ: AnyType) -> T:
        return self.visit_proper_type(typ)

    @ta.override
    def visit_uninhabited_type(self, typ: UninhabitedType) -> T:
        return self.visit_proper_type(typ)

    @ta.override
    def visit_none_type(self, typ: NoneType) -> T:
        return self.visit_proper_type(typ)

    @ta.override
    def visit_erased_type(self, typ: ErasedType) -> T:
        return self.visit_proper_type(typ)

    @ta.override
    def visit_deleted_type(self, typ: DeletedType) -> T:
        return self.visit_proper_type(typ)

    @ta.override
    def visit_instance(self, typ: Instance) -> T:
        return self.visit_proper_type(typ)

    @ta.override
    def visit_parameters(self, typ: Parameters) -> T:
        return self.visit_proper_type(typ)

    def visit_function_like(self, typ: FunctionLike) -> T:
        return self.visit_proper_type(typ)

    @ta.override
    def visit_callable_type(self, typ: CallableType) -> T:
        return self.visit_function_like(typ)

    @ta.override
    def visit_overloaded(self, typ: Overloaded) -> T:
        return self.visit_function_like(typ)

    @ta.override
    def visit_tuple_type(self, typ: TupleType) -> T:
        return self.visit_proper_type(typ)

    @ta.override
    def visit_typeddict_type(self, typ: TypedDictType) -> T:
        return self.visit_proper_type(typ)

    @ta.override
    def visit_raw_expression_type(self, typ: RawExpressionType) -> T:
        return self.visit_proper_type(typ)

    @ta.override
    def visit_literal_type(self, typ: LiteralType) -> T:
        return self.visit_proper_type(typ)

    @ta.override
    def visit_union_type(self, typ: UnionType) -> T:
        return self.visit_proper_type(typ)

    @ta.override
    def visit_partial_type(self, typ: PartialType) -> T:
        return self.visit_proper_type(typ)

    @ta.override
    def visit_ellipsis_type(self, typ: EllipsisType) -> T:
        return self.visit_proper_type(typ)

    @ta.override
    def visit_type_type(self, typ: TypeType) -> T:
        return self.visit_proper_type(typ)

    @ta.override
    def visit_placeholder_type(self, typ: PlaceholderType) -> T:
        return self.visit_proper_type(typ)


##


@mypyc_attr(allow_interpreted_subclasses=True)
class TypeTranslator(TypeVisitor[Type]):
    def translate_types(self, typs: list[Type]) -> list[Type]:
        return [typ.accept(self) for typ in typs]

    def visit_type_alias_type(self, typ: TypeAliasType) -> Type:
        return TypeAliasType(typ._alias, self.translate_types(typ._args))

    def visit_type_guarded_type(self, typ: TypeGuardedType) -> Type:
        return TypeGuardedType(typ._type_guard.accept(self))

    def visit_annotated_type(self, typ: AnnotatedType) -> Type:
        return AnnotatedType(typ._item.accept(self), typ._metadata)

    def visit_required_type(self, typ: RequiredType) -> Type:
        return RequiredType(typ._item.accept(self), required=typ._required)

    def visit_read_only_type(self, typ: ReadOnlyType) -> Type:
        return ReadOnlyType(typ._item.accept(self))

    def visit_type_var(self, typ: TypeVarType) -> Type:
        return typ

    def visit_param_spec(self, typ: ParamSpecType) -> Type:
        return typ

    def visit_type_var_tuple(self, typ: TypeVarTupleType) -> Type:
        return typ

    def visit_unbound_type(self, typ: UnboundType) -> Type:
        return UnboundType(typ._name, self.translate_types(typ._args))

    def visit_callable_argument(self, typ: CallableArgument) -> Type:
        return CallableArgument(typ._typ.accept(self), typ._name, typ._constructor)

    def visit_type_list(self, typ: TypeList) -> Type:
        return TypeList(self.translate_types(typ._items))

    def visit_unpack_type(self, typ: UnpackType) -> Type:
        return UnpackType(typ._type.accept(self))

    def visit_any(self, typ: AnyType) -> Type:
        return typ

    def visit_uninhabited_type(self, typ: UninhabitedType) -> Type:
        return typ

    def visit_none_type(self, typ: NoneType) -> Type:
        return typ

    def visit_erased_type(self, typ: ErasedType) -> Type:
        return typ

    def visit_deleted_type(self, typ: DeletedType) -> Type:
        return typ

    def visit_instance(self, typ: Instance) -> Type:
        last_known_value = None
        if typ._last_known_value is not None:
            translated_lkv = typ._last_known_value.accept(self)
            if not isinstance(translated_lkv, LiteralType):
                raise ReflectionTypeError(translated_lkv)
            last_known_value = translated_lkv
        return Instance(
            typ._type,
            self.translate_types(typ._args),
            last_known_value=last_known_value,
            extra_attrs=typ._extra_attrs,
        )

    def visit_parameters(self, typ: Parameters) -> Type:
        return Parameters(
            self.translate_types(typ._arg_types),
            typ._arg_kinds.copy(),
            typ._arg_names.copy(),
        )

    def visit_callable_type(self, typ: CallableType) -> Type:
        fallback = typ._fallback.accept(self)
        if not isinstance(fallback, Instance):
            raise ReflectionTypeError(fallback)
        return CallableType(
            self.translate_types(typ._arg_types),
            typ._arg_kinds.copy(),
            typ._arg_names.copy(),
            typ._ret_type.accept(self),
            fallback,
            variables=typ._variables.copy(),
            is_ellipsis_args=typ._is_ellipsis_args,
        )

    def visit_overloaded(self, typ: Overloaded) -> Type:
        items: list[CallableType] = []
        for item in typ._items:
            translated = item.accept(self)
            if not isinstance(translated, CallableType):
                raise ReflectionTypeError(translated)
            items.append(translated)
        return Overloaded(items)

    def visit_tuple_type(self, typ: TupleType) -> Type:
        partial_fallback = typ._partial_fallback.accept(self)
        if not isinstance(partial_fallback, Instance):
            raise ReflectionTypeError(partial_fallback)
        return TupleType(self.translate_types(typ._items), partial_fallback)

    def visit_typeddict_type(self, typ: TypedDictType) -> Type:
        fallback = typ._fallback.accept(self)
        if not isinstance(fallback, Instance):
            raise ReflectionTypeError(fallback)
        return TypedDictType(
            {name: item.accept(self) for name, item in typ._items.items()},
            typ._required_keys.copy(),
            typ._readonly_keys.copy(),
            fallback,
        )

    def visit_raw_expression_type(self, typ: RawExpressionType) -> Type:
        return typ

    def visit_literal_type(self, typ: LiteralType) -> Type:
        fallback = typ._fallback.accept(self)
        if not isinstance(fallback, Instance):
            raise ReflectionTypeError(fallback)
        return LiteralType(typ._value, fallback)

    def visit_union_type(self, typ: UnionType) -> Type:
        return UnionType(self.translate_types(typ._items))

    def visit_partial_type(self, typ: PartialType) -> Type:
        value_type = None if typ._value_type is None else typ._value_type.accept(self)
        return PartialType(typ._type, typ._var, value_type)

    def visit_ellipsis_type(self, typ: EllipsisType) -> Type:
        return typ

    def visit_type_type(self, typ: TypeType) -> Type:
        return TypeType(typ._item.accept(self))

    def visit_placeholder_type(self, typ: PlaceholderType) -> Type:
        return PlaceholderType(typ._fullname, self.translate_types(typ._args))


##


@mypyc_attr(allow_interpreted_subclasses=True)
class TypeQuery(TypeVisitor[T]):
    __slots__ = (
        'seen_aliases',
        'skip_alias_target',
    )

    def __init__(self) -> None:
        super().__init__()

        self.seen_aliases: set[TypeAliasType] | None = None
        self.skip_alias_target = False

    def strategy(self, items: list[T]) -> T:
        raise NotImplementedError

    def query_types(self, typs: ta.Iterable[Type]) -> T:
        return self.strategy([typ.accept(self) for typ in typs])

    def visit_type_alias_type(self, typ: TypeAliasType) -> T:
        if self.skip_alias_target or typ._alias is None:
            return self.query_types(typ._args)

        if self.seen_aliases is None:
            self.seen_aliases = set()
        elif typ in self.seen_aliases:
            return self.strategy([])

        self.seen_aliases.add(typ)
        return self.query_types([*typ._args, typ._alias._target])

    def visit_type_guarded_type(self, typ: TypeGuardedType) -> T:
        return typ._type_guard.accept(self)

    def visit_annotated_type(self, typ: AnnotatedType) -> T:
        return typ._item.accept(self)

    def visit_required_type(self, typ: RequiredType) -> T:
        return typ._item.accept(self)

    def visit_read_only_type(self, typ: ReadOnlyType) -> T:
        return typ._item.accept(self)

    def visit_type_var(self, typ: TypeVarType) -> T:
        return self.query_types([typ._upper_bound, typ._default, *typ._values])

    def visit_param_spec(self, typ: ParamSpecType) -> T:
        return self.query_types([typ._upper_bound, typ._default])

    def visit_type_var_tuple(self, typ: TypeVarTupleType) -> T:
        return self.query_types([typ._upper_bound, typ._default, typ._tuple_fallback])

    def visit_unbound_type(self, typ: UnboundType) -> T:
        return self.query_types(typ._args)

    def visit_callable_argument(self, typ: CallableArgument) -> T:
        return typ.typ.accept(self)

    def visit_type_list(self, typ: TypeList) -> T:
        return self.query_types(typ._items)

    def visit_unpack_type(self, typ: UnpackType) -> T:
        return typ._type.accept(self)

    def visit_any(self, typ: AnyType) -> T:
        return self.strategy([])

    def visit_uninhabited_type(self, typ: UninhabitedType) -> T:
        return self.strategy([])

    def visit_none_type(self, typ: NoneType) -> T:
        return self.strategy([])

    def visit_erased_type(self, typ: ErasedType) -> T:
        return self.strategy([])

    def visit_deleted_type(self, typ: DeletedType) -> T:
        return self.strategy([])

    def visit_instance(self, typ: Instance) -> T:
        if typ._last_known_value is None:
            return self.query_types(typ._args)
        return self.query_types([*typ._args, typ._last_known_value])

    def visit_parameters(self, typ: Parameters) -> T:
        return self.query_types(typ._arg_types)

    def visit_callable_type(self, typ: CallableType) -> T:
        return self.query_types([*typ._arg_types, typ._ret_type])

    def visit_overloaded(self, typ: Overloaded) -> T:
        return self.query_types(typ._items)

    def visit_tuple_type(self, typ: TupleType) -> T:
        return self.query_types([*typ._items, typ._partial_fallback])

    def visit_typeddict_type(self, typ: TypedDictType) -> T:
        return self.query_types([*typ._items.values(), typ._fallback])

    def visit_raw_expression_type(self, typ: RawExpressionType) -> T:
        return self.strategy([])

    def visit_literal_type(self, typ: LiteralType) -> T:
        return typ._fallback.accept(self)

    def visit_union_type(self, typ: UnionType) -> T:
        return self.query_types(typ._items)

    def visit_partial_type(self, typ: PartialType) -> T:
        if typ._value_type is None:
            return self.strategy([])
        return typ._value_type.accept(self)

    def visit_ellipsis_type(self, typ: EllipsisType) -> T:
        return self.strategy([])

    def visit_type_type(self, typ: TypeType) -> T:
        return typ._item.accept(self)

    def visit_placeholder_type(self, typ: PlaceholderType) -> T:
        return self.query_types(typ._args)


#


class BoolTypeQueryMode(enum.Enum):
    ANY = 'any'
    ALL = 'all'


@mypyc_attr(allow_interpreted_subclasses=True)
class BoolTypeQuery(TypeQuery[bool]):
    __slots__ = (
        'mode',
        'default',
    )

    def __init__(self, mode: BoolTypeQueryMode) -> None:
        super().__init__()

        if mode is BoolTypeQueryMode.ANY:
            self.default = False
        elif mode is BoolTypeQueryMode.ALL:
            self.default = True
        else:
            raise ReflectionValueError(mode)

        self.mode = mode

    def reset(self) -> None:
        self.seen_aliases = None

    def strategy(self, items: list[bool]) -> bool:
        if not items:
            return self.default
        if self.mode is BoolTypeQueryMode.ANY:
            return any(items)
        return all(items)
