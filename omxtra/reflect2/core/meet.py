# ruff: noqa: SLF001
import typing as ta

from ..errors import UnsupportedTypeOperationError
from .subtypes import is_same_type
from .subtypes import is_structural_subtype
from .subtypes import is_structurally_equivalent
from .subtypes import is_subtype
from .typeops import make_simplified_union
from .types import _ANY_TYPES
from .types import _UNINHABITED_TYPE
from .types import AnnotatedType
from .types import AnyType
from .types import CallableType
from .types import Overloaded
from .types import TupleType
from .types import Type
from .types import TypedDictType
from .types import TypeGuardedType
from .types import TypeOfAny
from .types import TypeType
from .types import TypeVarTupleType
from .types import UninhabitedType
from .types import UnionType
from .types import UnpackType


SubtypeFn: ta.TypeAlias = ta.Callable[[Type, Type], bool]
SameFn: ta.TypeAlias = ta.Callable[[Type, Type], bool]
JoinFn: ta.TypeAlias = ta.Callable[[Type, Type], Type]


##


def meet_types(left: Type, right: Type) -> Type:
    from .join import join_types

    return _meet_types(left, right, is_subtype, is_same_type, join_types)


def structural_meet_types(left: Type, right: Type) -> Type:
    from .join import structural_join_types

    return _meet_types(left, right, is_structural_subtype, is_structurally_equivalent, structural_join_types)


def _meet_types(
        left: Type,
        right: Type,
        subtype_fn: SubtypeFn,
        same_fn: SameFn,
        join_fn: JoinFn,
) -> Type:
    if isinstance(left, TypeGuardedType):
        return _meet_types(left._type_guard, right, subtype_fn, same_fn, join_fn)
    if isinstance(right, TypeGuardedType):
        return _meet_types(left, right._type_guard, subtype_fn, same_fn, join_fn)
    if isinstance(left, AnnotatedType):
        return _meet_types(left._item, right, subtype_fn, same_fn, join_fn)
    if isinstance(right, AnnotatedType):
        return _meet_types(left, right._item, subtype_fn, same_fn, join_fn)

    if same_fn(left, right):
        return left

    if isinstance(left, AnyType):
        return right
    if isinstance(right, AnyType):
        return left

    if isinstance(left, UnionType) or isinstance(right, UnionType):
        return _meet_union_types(left, right, subtype_fn, same_fn, join_fn)

    if isinstance(left, TypeType) and isinstance(right, TypeType):
        return TypeType(_meet_types(left._item, right._item, subtype_fn, same_fn, join_fn))

    if isinstance(left, Overloaded) and isinstance(right, Overloaded):
        return _meet_overloaded_types(left, right, same_fn, join_fn, subtype_fn)

    if isinstance(left, TupleType) and isinstance(right, TupleType):
        return _meet_tuple_types(left, right, subtype_fn, same_fn, join_fn)

    left_subtype = _try_is_subtype(left, right, subtype_fn)
    if left_subtype is True:
        return left

    right_subtype = _try_is_subtype(right, left, subtype_fn)
    if right_subtype is True:
        return right

    if left_subtype is None or right_subtype is None:
        raise UnsupportedTypeOperationError(f'Unsupported meet: {left!r} & {right!r}')

    if isinstance(left, Overloaded) or isinstance(right, Overloaded):
        raise UnsupportedTypeOperationError(f'Unsupported meet: {left!r} & {right!r}')

    if isinstance(left, CallableType) and isinstance(right, CallableType):
        if (callable_meet := _meet_callable_types_or_none(left, right, same_fn, join_fn, subtype_fn)) is not None:
            return callable_meet

    if isinstance(left, TypedDictType) and isinstance(right, TypedDictType):
        return _meet_typed_dicts(left, right, subtype_fn, same_fn, join_fn)

    return _UNINHABITED_TYPE


def meet_type_list(items: list[Type]) -> Type:
    if not items:
        return _ANY_TYPES[TypeOfAny.SPECIAL_FORM]

    met = items[0]
    for item in items[1:]:
        met = meet_types(met, item)
    return met


def structural_meet_type_list(items: list[Type]) -> Type:
    if not items:
        return _ANY_TYPES[TypeOfAny.SPECIAL_FORM]

    met = items[0]
    for item in items[1:]:
        met = structural_meet_types(met, item)
    return met


def _meet_union_types(
        left: Type,
        right: Type,
        subtype_fn: SubtypeFn,
        same_fn: SameFn,
        join_fn: JoinFn,
) -> Type:
    left_items = left._items if isinstance(left, UnionType) else [left]
    right_items = right._items if isinstance(right, UnionType) else [right]
    items: list[Type] = []

    for left_item in left_items:
        for right_item in right_items:
            item = _meet_types(left_item, right_item, subtype_fn, same_fn, join_fn)
            if not _is_uninhabited_meet_result(item):
                items.append(item)

    if not items:
        return _UNINHABITED_TYPE
    return _make_simplified_union(items, subtype_fn, same_fn)


def _is_uninhabited_meet_result(typ: Type) -> bool:
    return (
        isinstance(typ, UninhabitedType) or
        (isinstance(typ, TypeType) and isinstance(typ._item, UninhabitedType))
    )


def _make_simplified_union(typs: list[Type], subtype_fn: SubtypeFn, same_fn: SameFn) -> Type:
    if subtype_fn is is_subtype and same_fn is is_same_type:
        return make_simplified_union(typs)

    result: list[Type] = []
    for typ in typs:
        if any(same_fn(typ, seen) for seen in result):
            continue
        if any(_is_subtype_or_false(typ, seen, subtype_fn) for seen in result):
            continue
        result = [
            seen
            for seen in result
            if not _is_subtype_or_false(seen, typ, subtype_fn)
        ]
        result.append(typ)

    if len(result) > 1:
        return UnionType(result)
    if len(result) == 1:
        return result[0]
    return _UNINHABITED_TYPE


def _is_subtype_or_false(left: Type, right: Type, subtype_fn: SubtypeFn) -> bool:
    try:
        return subtype_fn(left, right)
    except UnsupportedTypeOperationError:
        return False


def _try_is_subtype(left: Type, right: Type, subtype_fn: SubtypeFn) -> bool | None:
    try:
        return subtype_fn(left, right)
    except UnsupportedTypeOperationError:
        return None


def _meet_callable_types_or_none(
        left: CallableType,
        right: CallableType,
        same_fn: SameFn,
        join_fn: JoinFn,
        subtype_fn: SubtypeFn,
) -> CallableType | None:
    if not _has_same_simple_callable_shape(left, right):
        return None

    if not same_fn(left._fallback, right._fallback):
        raise UnsupportedTypeOperationError(f'Unsupported Callable meet with different fallbacks: {left!r} & {right!r}')

    return CallableType(
        [
            join_fn(left_arg, right_arg)
            for left_arg, right_arg in zip(left._arg_types, right._arg_types)
        ],
        list(left._arg_kinds),
        list(left._arg_names),
        _meet_types(left._ret_type, right._ret_type, subtype_fn, same_fn, join_fn),
        left._fallback,
    )


def _has_same_simple_callable_shape(left: CallableType, right: CallableType) -> bool:
    return (
        not left._variables
        and not right._variables
        and not left._is_ellipsis_args
        and not right._is_ellipsis_args
        and left._arg_kinds == right._arg_kinds
        and left._arg_names == right._arg_names
        and len(left._arg_types) == len(right._arg_types)
    )


def _meet_overloaded_types(
        left: Overloaded,
        right: Overloaded,
        same_fn: SameFn,
        join_fn: JoinFn,
        subtype_fn: SubtypeFn,
) -> Overloaded:
    if len(left._items) != len(right._items):
        raise UnsupportedTypeOperationError(
            f'Unsupported Overloaded meet with mismatched item counts: {left!r} & {right!r}',
        )

    items: list[CallableType] = []
    for left_item, right_item in zip(left._items, right._items):
        item = _meet_callable_types_or_none(left_item, right_item, same_fn, join_fn, subtype_fn)
        if item is None:
            raise UnsupportedTypeOperationError(f'Unsupported Overloaded meet: {left!r} & {right!r}')
        items.append(item)

    return Overloaded(items)


def _meet_tuple_types(
        left: TupleType,
        right: TupleType,
        subtype_fn: SubtypeFn,
        same_fn: SameFn,
        join_fn: JoinFn,
) -> Type:
    if _has_variadic_tuple_item(left) or _has_variadic_tuple_item(right):
        raise UnsupportedTypeOperationError(f'Unsupported variadic Tuple meet: {left!r} & {right!r}')

    if len(left._items) != len(right._items):
        return _UNINHABITED_TYPE

    if not same_fn(left._partial_fallback, right._partial_fallback):
        raise UnsupportedTypeOperationError(f'Unsupported Tuple meet with different fallbacks: {left!r} & {right!r}')

    items: list[Type] = []
    for left_item, right_item in zip(left._items, right._items):
        item = _meet_types(left_item, right_item, subtype_fn, same_fn, join_fn)
        if _is_uninhabited_meet_result(item):
            return _UNINHABITED_TYPE
        items.append(item)

    return TupleType(items, left._partial_fallback)


def _has_variadic_tuple_item(typ: TupleType) -> bool:
    return any(isinstance(item, (UnpackType, TypeVarTupleType)) for item in typ._items)


def _meet_typed_dicts(
        left: TypedDictType,
        right: TypedDictType,
        subtype_fn: SubtypeFn,
        same_fn: SameFn,
        join_fn: JoinFn,
) -> TypedDictType:
    items: dict[str, Type] = {}

    for name in left._items.keys() | right._items.keys():
        if name not in left._items:
            items[name] = right._items[name]
            continue

        if name not in right._items:
            items[name] = left._items[name]
            continue

        items[name] = _meet_typed_dict_item(
            name,
            left._items[name],
            name in left._readonly_keys,
            right._items[name],
            name in right._readonly_keys,
            subtype_fn,
            same_fn,
            join_fn,
        )

    return TypedDictType(
        items,
        left._required_keys | right._required_keys,
        left._readonly_keys | right._readonly_keys,
        left._fallback,
    )


def _meet_typed_dict_item(
        name: str,
        left: Type,
        left_readonly: bool,
        right: Type,
        right_readonly: bool,
        subtype_fn: SubtypeFn,
        same_fn: SameFn,
        join_fn: JoinFn,
) -> Type:
    if same_fn(left, right):
        return left

    if left_readonly and right_readonly:
        return _meet_types(left, right, subtype_fn, same_fn, join_fn)

    if not left_readonly and not right_readonly:
        raise UnsupportedTypeOperationError(
            f'Unsupported mutable TypedDict item meet for {name!r}: {left!r} & {right!r}',
        )

    mutable_item = right if left_readonly else left
    readonly_item = left if left_readonly else right
    if subtype_fn(mutable_item, readonly_item):
        return mutable_item

    raise UnsupportedTypeOperationError(
        f'Unsupported mixed-readonly TypedDict item meet for {name!r}: {left!r} & {right!r}',
    )
