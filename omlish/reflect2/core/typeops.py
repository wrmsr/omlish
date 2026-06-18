# ruff: noqa: SLF001
import typing as ta

from ..errors import ReflectionTypeError
from .symbols import TypeAlias
from .types import _UNINHABITED_TYPE
from .types import AnnotatedType
from .types import AnyType
from .types import CallableArgument
from .types import CallableType
from .types import Instance
from .types import LiteralType
from .types import LiteralValue
from .types import Overloaded
from .types import Parameters
from .types import ParamSpecType
from .types import PartialType
from .types import PlaceholderType
from .types import ProperType
from .types import ReadOnlyType
from .types import RequiredType
from .types import TupleType
from .types import Type
from .types import TypeAliasType
from .types import TypedDictType
from .types import TypeGuardedType
from .types import TypeList
from .types import TypeType
from .types import TypeVarTupleType
from .types import TypeVarType
from .types import UnboundType
from .types import UnionType
from .types import UnpackType
from .typevisitor import BoolTypeQuery
from .typevisitor import BoolTypeQueryMode
from .typevisitor import DefaultTypeVisitor


##


class RecursiveTypeError(ReflectionTypeError):
    pass


@ta.overload
def get_proper_type(typ: None) -> None:
    ...


@ta.overload
def get_proper_type(typ: Type) -> ProperType:
    ...


def get_proper_type(typ: Type | None) -> ProperType | None:
    if typ is None:
        return None

    if isinstance(typ, TypeGuardedType):
        typ = typ._type_guard
    if isinstance(typ, AnnotatedType):
        typ = typ._item

    seen_aliases: set[TypeAlias] = set()
    while isinstance(typ, TypeAliasType):
        if typ._alias is None:
            raise ReflectionTypeError('unfixed type alias')
        if typ._alias in seen_aliases or typ.is_recursive:
            raise RecursiveTypeError(typ._alias._fullname)
        seen_aliases.add(typ._alias)
        typ = get_type_alias_target(typ)

    if not isinstance(typ, ProperType):
        raise ReflectionTypeError(typ)

    return typ


def get_type_alias_target(typ: TypeAliasType) -> Type:
    if typ._alias is None:
        raise ReflectionTypeError('unfixed type alias')

    if not typ._args:
        return typ._alias._target

    if len(typ._args) != len(typ._alias._alias_tvars):
        raise ReflectionTypeError(typ)

    from .substitute import substitute_type

    return substitute_type(typ._alias._target, dict(zip(typ._alias._alias_tvars, typ._args)))


@ta.overload
def get_proper_types(typs: ta.Sequence[Type]) -> list[ProperType]:
    ...


@ta.overload
def get_proper_types(typs: ta.Sequence[Type | None]) -> list[ProperType | None]:
    ...


def get_proper_types(
        typs: ta.Sequence[Type] | ta.Sequence[Type | None],
) -> list[ProperType] | list[ProperType | None]:
    return [get_proper_type(typ) for typ in typs]


##


class HasTypeVars(BoolTypeQuery):
    def __init__(self) -> None:
        super().__init__(BoolTypeQueryMode.ANY)

        self.skip_alias_target = True

    def visit_type_var(self, typ: TypeVarType) -> bool:
        return True

    def visit_type_var_tuple(self, typ: TypeVarTupleType) -> bool:
        return True

    def visit_param_spec(self, typ: ParamSpecType) -> bool:
        return True


def has_type_vars(typ: Type) -> bool:
    return typ.accept(HasTypeVars())


##


def get_literal_values(typ: Type) -> list[LiteralValue]:
    values = get_literal_values_or_none(typ)
    if values is None:
        raise ReflectionTypeError(f'Type is not a finite literal value set: {typ!r}')
    return values


def get_literal_values_or_none(typ: Type) -> list[LiteralValue] | None:
    typ = get_proper_type(typ)
    if isinstance(typ, LiteralType):
        return [typ._value]

    if isinstance(typ, UnionType):
        values: list[LiteralValue] = []
        for item in typ._items:
            item_values = get_literal_values_or_none(item)
            if item_values is None:
                return None
            values.extend(item_values)
        return values

    return None


##


def collect_aliases(typ: Type) -> list[TypeAlias]:
    visitor = _CollectAliasesVisitor()
    typ.accept(visitor)
    return visitor.aliases


def is_recursive_alias(alias: TypeAlias) -> bool:
    return _contains_alias(alias._target, alias, set())


class _CollectAliasesVisitor(DefaultTypeVisitor[None]):
    __slots__ = (
        'aliases',
        'seen',
    )

    def __init__(self, seen: set[TypeAlias] | None = None) -> None:
        super().__init__()

        self.aliases: list[TypeAlias] = []
        self.seen = set() if seen is None else seen

    def collect_types(self, typs: ta.Iterable[Type]) -> None:
        for typ in typs:
            typ.accept(self)

    def visit_type(self, typ: Type) -> None:
        pass

    def visit_type_alias_type(self, typ: TypeAliasType) -> None:
        if typ._alias is not None:
            self.aliases.append(typ._alias)
            if typ._alias not in self.seen:
                self.seen.add(typ._alias)
                typ._alias._target.accept(self)
        self.collect_types(typ._args)

    def visit_type_guarded_type(self, typ: TypeGuardedType) -> None:
        typ._type_guard.accept(self)

    def visit_annotated_type(self, typ: AnnotatedType) -> None:
        typ._item.accept(self)

    def visit_required_type(self, typ: RequiredType) -> None:
        typ._item.accept(self)

    def visit_read_only_type(self, typ: ReadOnlyType) -> None:
        typ._item.accept(self)

    def visit_type_type(self, typ: TypeType) -> None:
        typ._item.accept(self)

    def visit_unpack_type(self, typ: UnpackType) -> None:
        typ._type.accept(self)

    def visit_type_var(self, typ: TypeVarType) -> None:
        typ._upper_bound.accept(self)
        typ._default.accept(self)
        self.collect_types(typ._values)

    def visit_param_spec(self, typ: ParamSpecType) -> None:
        typ._upper_bound.accept(self)
        typ._default.accept(self)

    def visit_type_var_tuple(self, typ: TypeVarTupleType) -> None:
        typ._upper_bound.accept(self)
        typ._default.accept(self)
        typ._tuple_fallback.accept(self)

    def visit_unbound_type(self, typ: UnboundType) -> None:
        self.collect_types(typ._args)

    def visit_callable_argument(self, typ: CallableArgument) -> None:
        typ._typ.accept(self)

    def visit_type_list(self, typ: TypeList) -> None:
        self.collect_types(typ._items)

    def visit_instance(self, typ: Instance) -> None:
        self.collect_types(typ._args)
        if typ._last_known_value is not None:
            typ._last_known_value.accept(self)

    def visit_parameters(self, typ: Parameters) -> None:
        self.collect_types(typ._arg_types)

    def visit_callable_type(self, typ: CallableType) -> None:
        self.collect_types(typ._arg_types)
        typ._ret_type.accept(self)
        typ._fallback.accept(self)
        self.collect_types(typ._variables)

    def visit_overloaded(self, typ: Overloaded) -> None:
        self.collect_types(typ._items)

    def visit_tuple_type(self, typ: TupleType) -> None:
        self.collect_types(typ._items)
        typ._partial_fallback.accept(self)

    def visit_typeddict_type(self, typ: TypedDictType) -> None:
        for item in typ._items.values():
            item.accept(self)
        typ._fallback.accept(self)

    def visit_literal_type(self, typ: LiteralType) -> None:
        typ._fallback.accept(self)

    def visit_union_type(self, typ: UnionType) -> None:
        self.collect_types(typ._items)

    def visit_partial_type(self, typ: PartialType) -> None:
        if typ._value_type is not None:
            typ._value_type.accept(self)

    def visit_placeholder_type(self, typ: PlaceholderType) -> None:
        self.collect_types(typ._args)


def _contains_alias(
        typ: Type,
        target: TypeAlias,
        seen: set[TypeAlias],
) -> bool:
    if isinstance(typ, TypeAliasType):
        if typ._alias is target:
            return True
        if typ._alias is not None and typ._alias not in seen:
            seen.add(typ._alias)
            if _contains_alias(typ._alias._target, target, seen):
                return True
        return any(_contains_alias(arg, target, seen) for arg in typ._args)

    visitor = _CollectAliasesVisitor(seen)
    typ.accept(visitor)
    return any(alias is target for alias in visitor.aliases)


##


def flatten_nested_unions(
        typs: ta.Sequence[Type],
        *,
        handle_type_alias_type: bool = True,
        handle_recursive: bool = True,
) -> list[Type]:
    flat_items: list[Type] = []

    for typ in typs:
        if handle_type_alias_type and isinstance(typ, TypeAliasType):
            if not handle_recursive and typ.is_recursive:
                ptyp: Type = typ
            else:
                ptyp = get_proper_type(typ)
        else:
            ptyp = typ

        if isinstance(ptyp, UnionType):
            flat_items.extend(
                flatten_nested_unions(
                    ptyp._items,
                    handle_type_alias_type=handle_type_alias_type,
                    handle_recursive=handle_recursive,
                ),
            )
        else:
            flat_items.append(typ)

    return flat_items


def try_contracting_literals_in_union(typs: ta.Sequence[Type]) -> list[ProperType]:
    proper_types = [get_proper_type(typ) for typ in typs]
    result: list[ProperType] = []
    bool_literals_by_fullname: dict[str, list[int]] = {}

    for typ in proper_types:
        if typ is None:
            raise ReflectionTypeError(typ)

        result.append(typ)
        if isinstance(typ, LiteralType) and isinstance(typ._value, bool):
            indexes = bool_literals_by_fullname.setdefault(typ._fallback._type._fullname, [])
            indexes.append(len(result) - 1)

    delete_indexes: set[int] = set()
    for indexes in bool_literals_by_fullname.values():
        values: set[LiteralValue] = set()
        for index in indexes:
            result_item = result[index]
            if isinstance(result_item, LiteralType):
                values.add(result_item._value)
        if values == {False, True}:
            first_index = indexes[0]
            first = result[first_index]
            if not isinstance(first, LiteralType):
                raise ReflectionTypeError(first)
            result[first_index] = first._fallback
            delete_indexes.update(indexes[1:])

    if not delete_indexes:
        return result

    return [typ for index, typ in enumerate(result) if index not in delete_indexes]


def remove_duplicate_union_items(typs: ta.Sequence[Type]) -> list[Type]:
    from .subtypes import is_same_type

    result: list[Type] = []
    for typ in typs:
        if not any(is_same_type(typ, seen) for seen in result):
            result.append(typ)
    return result


def remove_redundant_union_items(typs: ta.Sequence[Type]) -> list[Type]:
    from .subtypes import is_subtype_or_false

    result: list[Type] = []
    for typ in typs:
        if isinstance(typ, AnyType):
            result.append(typ)
            continue

        if any(
                not isinstance(seen, AnyType)
                and is_subtype_or_false(typ, seen)
                for seen in result
        ):
            continue
        result = [
            seen
            for seen in result
            if isinstance(seen, AnyType) or not is_subtype_or_false(seen, typ)
        ]
        result.append(typ)
    return result


@ta.overload
def make_union(typs: ta.Sequence[ProperType]) -> ProperType:
    ...


@ta.overload
def make_union(typs: ta.Sequence[Type]) -> Type:
    ...


def make_union(typs: ta.Sequence[Type]) -> Type:
    flat_items = flatten_nested_unions(typs)
    if len(flat_items) > 1:
        return UnionType(flat_items)
    if len(flat_items) == 1:
        return flat_items[0]
    return _UNINHABITED_TYPE


def make_simplified_union(
        typs: ta.Sequence[Type],
        *,
        contract_literals: bool = True,
        handle_recursive: bool = True,
) -> Type:
    flat_items: ta.Sequence[Type] = flatten_nested_unions(typs, handle_recursive=handle_recursive)
    if contract_literals:
        flat_items = try_contracting_literals_in_union(flat_items)
    flat_items = remove_duplicate_union_items(flat_items)
    flat_items = remove_redundant_union_items(flat_items)
    return make_union(flat_items)
