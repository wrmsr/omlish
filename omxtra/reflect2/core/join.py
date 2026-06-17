# ruff: noqa: SLF001
import typing as ta

from ..errors import UnsupportedTypeOperationError
from .subtypes import is_same_type
from .subtypes import is_structural_subtype
from .subtypes import is_structurally_equivalent
from .subtypes import is_subtype
from .typeops import make_simplified_union
from .types import _UNINHABITED_TYPE
from .types import AnnotatedType
from .types import AnyType
from .types import CallableType
from .types import Overloaded
from .types import TupleType
from .types import Type
from .types import TypedDictType
from .types import TypeGuardedType
from .types import TypeType
from .types import TypeVarTupleType
from .types import UnionType
from .types import UnpackType


SubtypeFn: ta.TypeAlias = ta.Callable[[Type, Type], bool]
SameFn: ta.TypeAlias = ta.Callable[[Type, Type], bool]
MeetFn: ta.TypeAlias = ta.Callable[[Type, Type], Type]


##


def join_types(left: Type, right: Type) -> Type:
    from .meet import meet_types

    return _join_types(
        left,
        right,
        is_subtype,
        is_same_type,
        meet_types,
    )


def structural_join_types(left: Type, right: Type) -> Type:
    from .meet import structural_meet_types

    return _join_types(
        left,
        right,
        is_structural_subtype,
        is_structurally_equivalent,
        structural_meet_types,
    )


def _join_types(
        left: Type,
        right: Type,
        subtype_fn: SubtypeFn,
        same_fn: SameFn,
        meet_fn: MeetFn,
) -> Type:
    if isinstance(left, TypeGuardedType):
        return _join_types(left._type_guard, right, subtype_fn, same_fn, meet_fn)
    if isinstance(right, TypeGuardedType):
        return _join_types(left, right._type_guard, subtype_fn, same_fn, meet_fn)
    if isinstance(left, AnnotatedType):
        return _join_types(left._item, right, subtype_fn, same_fn, meet_fn)
    if isinstance(right, AnnotatedType):
        return _join_types(left, right._item, subtype_fn, same_fn, meet_fn)

    if same_fn(left, right):
        return left

    if isinstance(left, AnyType):
        return left
    if isinstance(right, AnyType):
        return right

    if isinstance(left, UnionType):
        return _make_simplified_union([*left._items, right], subtype_fn, same_fn)
    if isinstance(right, UnionType):
        return _make_simplified_union([left, *right._items], subtype_fn, same_fn)

    if isinstance(left, TypeType) and isinstance(right, TypeType):
        return TypeType(_join_types(left._item, right._item, subtype_fn, same_fn, meet_fn))

    if isinstance(left, Overloaded) and isinstance(right, Overloaded):
        return _join_overloaded_types(left, right, same_fn, meet_fn, subtype_fn)

    if isinstance(left, TupleType) and isinstance(right, TupleType):
        return _join_tuple_types(left, right, subtype_fn, same_fn, meet_fn)

    left_subtype = _try_is_subtype(left, right, subtype_fn)
    if left_subtype is True:
        return right

    right_subtype = _try_is_subtype(right, left, subtype_fn)
    if right_subtype is True:
        return left

    if left_subtype is None or right_subtype is None:
        raise UnsupportedTypeOperationError(f'Unsupported join: {left!r} | {right!r}')

    if isinstance(left, Overloaded) or isinstance(right, Overloaded):
        raise UnsupportedTypeOperationError(f'Unsupported join: {left!r} | {right!r}')

    if isinstance(left, CallableType) and isinstance(right, CallableType):
        if (callable_join := _join_callable_types_or_none(left, right, same_fn, meet_fn, subtype_fn)) is not None:
            return callable_join

    if isinstance(left, TypedDictType) and isinstance(right, TypedDictType):
        return _join_typed_dicts(left, right, subtype_fn, same_fn, meet_fn)

    return _make_simplified_union([left, right], subtype_fn, same_fn)


def join_type_list(items: ta.Sequence[Type]) -> Type:
    if not items:
        return _UNINHABITED_TYPE

    joined = items[0]
    for item in items[1:]:
        joined = join_types(joined, item)
    return joined


def structural_join_type_list(items: ta.Sequence[Type]) -> Type:
    if not items:
        return _UNINHABITED_TYPE

    joined = items[0]
    for item in items[1:]:
        joined = structural_join_types(joined, item)
    return joined


def _try_is_subtype(left: Type, right: Type, subtype_fn: SubtypeFn) -> bool | None:
    try:
        return subtype_fn(left, right)
    except UnsupportedTypeOperationError:
        return None


def _join_callable_types_or_none(
        left: CallableType,
        right: CallableType,
        same_fn: SameFn,
        meet_fn: MeetFn,
        subtype_fn: SubtypeFn,
) -> CallableType | None:
    if not _has_same_simple_callable_shape(left, right):
        return None

    if not same_fn(left._fallback, right._fallback):
        raise UnsupportedTypeOperationError(f'Unsupported Callable join with different fallbacks: {left!r} | {right!r}')

    return CallableType(
        [
            meet_fn(left_arg, right_arg)
            for left_arg, right_arg in zip(left._arg_types, right._arg_types)
        ],
        list(left._arg_kinds),
        list(left._arg_names),
        _join_types(left._ret_type, right._ret_type, subtype_fn, same_fn, meet_fn),
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


def _join_overloaded_types(
        left: Overloaded,
        right: Overloaded,
        same_fn: SameFn,
        meet_fn: MeetFn,
        subtype_fn: SubtypeFn,
) -> Overloaded:
    if len(left._items) != len(right._items):
        raise UnsupportedTypeOperationError(
            f'Unsupported Overloaded join with mismatched item counts: {left!r} | {right!r}',
        )

    items: list[CallableType] = []
    for left_item, right_item in zip(left._items, right._items):
        item = _join_callable_types_or_none(left_item, right_item, same_fn, meet_fn, subtype_fn)
        if item is None:
            raise UnsupportedTypeOperationError(f'Unsupported Overloaded join: {left!r} | {right!r}')
        items.append(item)

    return Overloaded(items)


def _join_tuple_types(
        left: TupleType,
        right: TupleType,
        subtype_fn: SubtypeFn,
        same_fn: SameFn,
        meet_fn: MeetFn,
) -> Type:
    if _has_variadic_tuple_item(left) or _has_variadic_tuple_item(right):
        raise UnsupportedTypeOperationError(f'Unsupported variadic Tuple join: {left!r} | {right!r}')

    if len(left._items) != len(right._items):
        return _make_simplified_union([left, right], subtype_fn, same_fn)

    if not same_fn(left._partial_fallback, right._partial_fallback):
        raise UnsupportedTypeOperationError(f'Unsupported Tuple join with different fallbacks: {left!r} | {right!r}')

    return TupleType(
        [
            _join_types(left_item, right_item, subtype_fn, same_fn, meet_fn)
            for left_item, right_item in zip(left._items, right._items)
        ],
        left._partial_fallback,
    )


def _has_variadic_tuple_item(typ: TupleType) -> bool:
    return any(isinstance(item, (UnpackType, TypeVarTupleType)) for item in typ._items)


def _join_typed_dicts(
        left: TypedDictType,
        right: TypedDictType,
        subtype_fn: SubtypeFn,
        same_fn: SameFn,
        meet_fn: MeetFn,
) -> TypedDictType:
    items: dict[str, Type] = {}
    required_keys: set[str] = set()
    readonly_keys: set[str] = set()

    for name in left._items.keys() & right._items.keys():
        left_readonly = name in left._readonly_keys
        right_readonly = name in right._readonly_keys

        if left_readonly or right_readonly:
            item = _join_types(left._items[name], right._items[name], subtype_fn, same_fn, meet_fn)
            readonly_keys.add(name)
        else:
            if not same_fn(left._items[name], right._items[name]):
                continue
            item = left._items[name]

        items[name] = item
        if name in left._required_keys and name in right._required_keys:
            required_keys.add(name)

    return TypedDictType(items, required_keys, readonly_keys, left._fallback)


def _make_simplified_union(typs: ta.Sequence[Type], subtype_fn: SubtypeFn, same_fn: SameFn) -> Type:
    if subtype_fn is is_subtype and same_fn is is_same_type:
        return make_simplified_union(typs)

    flat: list[Type] = []
    for typ in typs:
        if isinstance(typ, UnionType):
            flat.extend(typ._items)
        else:
            flat.append(typ)

    result: list[Type] = []
    for typ in flat:
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
