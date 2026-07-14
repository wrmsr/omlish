# ruff: noqa: A002 SLF001
import typing as ta

from ..errors import ReflectionTypeError
from ..errors import UnsupportedTypeOperationError
from .symbols import ArgKind
from .symbols import TypeAlias
from .symbols import TypeInfo
from .symbols import VarianceKind
from .typeops import get_type_alias_target
from .types import AnnotatedType
from .types import AnyType
from .types import CallableArgument
from .types import CallableType
from .types import DeletedType
from .types import EllipsisType
from .types import ErasedType
from .types import Instance
from .types import LiteralType
from .types import NoneType
from .types import Overloaded
from .types import Parameters
from .types import ParamSpecType
from .types import PartialType
from .types import PlaceholderType
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
from .types import TypeVarId
from .types import TypeVarLikeType
from .types import TypeVarTupleType
from .types import TypeVarType
from .types import UnboundType
from .types import UninhabitedType
from .types import UnionType
from .types import UnpackType


if ta.TYPE_CHECKING:
    from .substitute import SubstitutionMap


##


class TypeVarEnvFilter(ta.Protocol):
    def __call__(self, owner: Type, param: TypeVarLikeType, arg: Type) -> Type: ...


def get_base_instance(
        left: Instance,
        right_info: TypeInfo,
        *,
        env_filter: TypeVarEnvFilter | None = None,
) -> Instance | None:
    if left._type is right_info:
        return left

    if right_info not in left._type._mro:
        return None

    mapped = _map_instance_to_base(
        left,
        right_info,
        set(),
        env_filter=env_filter,
    )
    if mapped is not None:
        return mapped

    if right_info._type_vars:
        raise UnsupportedTypeOperationError(
            f'Generic base instance mapping is not implemented: {left!r} -> {right_info._fullname}',
        )

    return Instance(right_info, [])


def get_base_instance_or_none(left: Instance, right_info: TypeInfo) -> Instance | None:
    try:
        return get_base_instance(left, right_info)
    except UnsupportedTypeOperationError:
        return None


def get_base_args(left: Instance, right_info: TypeInfo) -> ta.Sequence[Type] | None:
    base = get_base_instance(left, right_info)
    if base is None:
        return None
    return base._args


def get_base_args_or_none(left: Instance, right_info: TypeInfo) -> ta.Sequence[Type] | None:
    base = get_base_instance_or_none(left, right_info)
    if base is None:
        return None
    return base._args


def _map_instance_to_base(
        left: Instance,
        right_info: TypeInfo,
        seen: set[TypeInfo],
        *,
        env_filter: TypeVarEnvFilter | None = None,
) -> Instance | None:
    if not left._type._bases:
        return None

    if left._type in seen:
        return None
    seen.add(left._type)

    if len(left._args) != len(left._type._type_vars):
        raise UnsupportedTypeOperationError(f'Cannot map generic base with mismatched args: {left!r}')

    from .substitute import substitute_type

    env: dict[TypeVarId | TypeVarLikeType, Type] = {}
    for type_var, arg in zip(left._type._type_vars, left._args):
        if env_filter is not None:
            arg = env_filter(left, type_var, arg)
        env[type_var] = arg
        env[type_var._id] = arg

    for base in left._type._bases:
        expanded = substitute_type(base, env)
        if not isinstance(expanded, Instance):
            raise UnsupportedTypeOperationError(f'Non-instance base is not implemented: {base!r}')
        if expanded._type is right_info:
            return expanded
        mapped = _map_instance_to_base(
            expanded,
            right_info,
            seen,
            env_filter=env_filter,
        )
        if mapped is not None:
            return mapped

    return None


##


class MroEntry:
    __slots__ = (
        '_info',
        '_instance',
        '_args',
    )

    def __init__(self, instance: Instance) -> None:
        super().__init__()

        self._info = instance._type
        self._instance = instance
        self._args = instance._args

    @property
    def info(self) -> TypeInfo:
        return self._info

    @property
    def instance(self) -> Instance:
        return self._instance

    @property
    def args(self) -> ta.Sequence[Type]:
        return self._args

    #

    def get_substitution_map(self) -> SubstitutionMap:
        owner_type_vars = self._info._type_vars
        if not owner_type_vars:
            return {}

        if len(owner_type_vars) != len(self._args):
            raise UnsupportedTypeOperationError(
                f'Cannot build mro substitution map with mismatched mro owner args: {self._instance!r}',
            )

        return dict(zip(owner_type_vars, self._args))

    def substitute_type(self, raw_type: Type) -> Type:
        subst_map = self.get_substitution_map()
        if not subst_map:
            return raw_type

        from .substitute import substitute_type

        return substitute_type(raw_type, subst_map)


class Mro(ta.Sequence[MroEntry]):
    __slots__ = (
        '_seq',
        '_by_info',
    )

    def __init__(self, entries: ta.Iterable[MroEntry]) -> None:
        super().__init__()

        self._seq = tuple(entries)

        self._by_info = {entry._info: entry for entry in self._seq}

    #

    def __len__(self) -> int:
        return len(self._seq)

    def __iter__(self) -> ta.Iterator[MroEntry]:
        return iter(self._seq)

    def __contains__(self, entry: object) -> bool:
        return entry in self._seq

    @ta.overload
    def __getitem__(self, index: int, /) -> MroEntry: ...

    @ta.overload
    def __getitem__(self, index: slice, /) -> ta.Sequence[MroEntry]: ...

    def __getitem__(self, index, /):
        return self._seq[index]

    #

    @property
    def by_info(self) -> ta.Mapping[TypeInfo, MroEntry]:
        return self._by_info


def get_mro_instances(
        left: Instance,
        *,
        env_filter: TypeVarEnvFilter | None = None,
) -> list[Instance]:
    instances: list[Instance] = []

    for info in left._type._mro:
        instance = get_base_instance(left, info, env_filter=env_filter)
        if instance is None:
            raise UnsupportedTypeOperationError(f'MRO entry is not mappable: {left!r} -> {info._fullname}')
        instances.append(instance)

    return instances


def get_mro_instances_or_none(left: Instance) -> list[Instance] | None:
    try:
        return get_mro_instances(left)
    except UnsupportedTypeOperationError:
        return None


def get_mro_entries(left: Instance) -> list[MroEntry]:
    return [
        MroEntry(instance)
        for instance in get_mro_instances(left)
    ]


def get_mro_entries_or_none(left: Instance) -> list[MroEntry] | None:
    instances = get_mro_instances_or_none(left)
    if instances is None:
        return None
    return [
        MroEntry(instance)
        for instance in instances
    ]


def get_mro(left: Type) -> Mro:
    if not isinstance(left, Instance):
        raise ReflectionTypeError(f'Unsupported MRO source: {left!r}')
    return Mro(get_mro_entries(left))


##


def is_equivalent(left: Type, right: Type) -> bool:
    return is_same_type(left, right)


def is_structurally_equivalent(left: Type, right: Type) -> bool:
    return _TypeComparer(False, expand_aliases=True).same(left, right)


def is_same_type(left: Type, right: Type) -> bool:
    return _TypeComparer(False, expand_aliases=False).same(left, right)


def is_alpha_equivalent(left: Type, right: Type) -> bool:
    return _TypeComparer(True, expand_aliases=False).same(left, right)


def is_alpha_structurally_equivalent(left: Type, right: Type) -> bool:
    return _TypeComparer(True, expand_aliases=True).same(left, right)


##


class _TypeComparer:
    def __init__(self, alpha: bool, *, expand_aliases: bool) -> None:
        super().__init__()

        self.alpha = alpha
        self.expand_aliases = expand_aliases
        self.left_to_right: dict[tuple[str, int, int], tuple[str, int, int]] = {}
        self.right_to_left: dict[tuple[str, int, int], tuple[str, int, int]] = {}
        self.assumed_alias_pairs: set[tuple[TypeAlias, TypeAlias]] = set()

    def same(self, left: Type, right: Type) -> bool:
        if left is right:
            return True

        if isinstance(left, TypeGuardedType):
            return self.same(left._type_guard, right)
        if isinstance(right, TypeGuardedType):
            return self.same(left, right._type_guard)
        if isinstance(left, AnnotatedType):
            return self.same(left._item, right)
        if isinstance(right, AnnotatedType):
            return self.same(left, right._item)

        if self.expand_aliases and (
                isinstance(left, TypeAliasType)
                or isinstance(right, TypeAliasType)
        ):
            return self.same_expanded_aliases(left, right)

        if not _is_supported_same_type_node(left):
            raise ReflectionTypeError(left)
        if not _is_supported_same_type_node(right):
            raise ReflectionTypeError(right)

        if type(left) is not type(right):
            return False

        if isinstance(left, TypeAliasType):
            if not isinstance(right, TypeAliasType):
                raise ReflectionTypeError(right, TypeAliasType)
            return self.same_type_alias_type(left, right)

        if isinstance(left, RequiredType):
            if not isinstance(right, RequiredType):
                raise ReflectionTypeError(right, RequiredType)
            return left._required == right._required and self.same(left._item, right._item)

        if isinstance(left, ReadOnlyType):
            if not isinstance(right, ReadOnlyType):
                raise ReflectionTypeError(right, ReadOnlyType)
            return self.same(left._item, right._item)

        if isinstance(left, TypeVarType):
            if not isinstance(right, TypeVarType):
                raise ReflectionTypeError(right, TypeVarType)
            return self.same_type_var_id(left._id, right._id)

        if isinstance(left, ParamSpecType):
            if not isinstance(right, ParamSpecType):
                raise ReflectionTypeError(right, ParamSpecType)
            return self.same_type_var_id(left._id, right._id)

        if isinstance(left, TypeVarTupleType):
            if not isinstance(right, TypeVarTupleType):
                raise ReflectionTypeError(right, TypeVarTupleType)
            return self.same_type_var_id(left._id, right._id)

        if isinstance(left, UnboundType):
            if not isinstance(right, UnboundType):
                raise ReflectionTypeError(right, UnboundType)
            return left._name == right._name and self.same_type_lists(left._args, right._args)

        if isinstance(left, CallableArgument):
            if not isinstance(right, CallableArgument):
                raise ReflectionTypeError(right, CallableArgument)
            return (
                left._name == right._name
                and left._constructor == right._constructor
                and self.same(left._typ, right._typ)
            )

        if isinstance(left, TypeList):
            if not isinstance(right, TypeList):
                raise ReflectionTypeError(right, TypeList)
            return self.same_type_lists(left._items, right._items)

        if isinstance(left, UnpackType):
            if not isinstance(right, UnpackType):
                raise ReflectionTypeError(right, UnpackType)
            return self.same(left._type, right._type)

        if isinstance(left, AnyType):
            if not isinstance(right, AnyType):
                raise ReflectionTypeError(right, AnyType)
            return left._type_of_any == right._type_of_any

        if isinstance(left, (UninhabitedType, NoneType, ErasedType, EllipsisType)):
            return True

        if isinstance(left, DeletedType):
            if not isinstance(right, DeletedType):
                raise ReflectionTypeError(right, DeletedType)
            return left._source == right._source

        if isinstance(left, Instance):
            if not isinstance(right, Instance):
                raise ReflectionTypeError(right, Instance)
            return (
                left._type is right._type
                and self.same_type_lists(left._args, right._args)
                and self.same_optional_type(left._last_known_value, right._last_known_value)
            )

        if isinstance(left, Parameters):
            if not isinstance(right, Parameters):
                raise ReflectionTypeError(right, Parameters)
            return (
                left._arg_kinds == right._arg_kinds
                and left._arg_names == right._arg_names
                and self.same_type_lists(left._arg_types, right._arg_types)
            )

        if isinstance(left, CallableType):
            if not isinstance(right, CallableType):
                raise ReflectionTypeError(right, CallableType)
            return (
                left._arg_kinds == right._arg_kinds
                and left._arg_names == right._arg_names
                and left._is_ellipsis_args == right._is_ellipsis_args
                and self.same_type_lists(left._arg_types, right._arg_types)
                and self.same(left._ret_type, right._ret_type)
                and self.same_type_lists(left._variables, right._variables)
                and self.same(left._fallback, right._fallback)
            )

        if isinstance(left, Overloaded):
            if not isinstance(right, Overloaded):
                raise ReflectionTypeError(right, Overloaded)
            return self.same_type_lists(left._items, right._items)

        if isinstance(left, TupleType):
            if not isinstance(right, TupleType):
                raise ReflectionTypeError(right, TupleType)
            return (
                self.same_type_lists(left._items, right._items)
                and self.same(left._partial_fallback, right._partial_fallback)
            )

        if isinstance(left, TypedDictType):
            if not isinstance(right, TypedDictType):
                raise ReflectionTypeError(right, TypedDictType)
            return (
                left._required_keys == right._required_keys
                and left._readonly_keys == right._readonly_keys
                and left._items.keys() == right._items.keys()
                and all(self.same(left._items[key], right._items[key]) for key in left._items)
                and self.same(left._fallback, right._fallback)
            )

        if isinstance(left, RawExpressionType):
            if not isinstance(right, RawExpressionType):
                raise ReflectionTypeError(right, RawExpressionType)
            return left._literal_value == right._literal_value and left._base_type_name == right._base_type_name

        if isinstance(left, LiteralType):
            if not isinstance(right, LiteralType):
                raise ReflectionTypeError(right, LiteralType)
            return left._value == right._value and self.same(left._fallback, right._fallback)

        if isinstance(left, UnionType):
            if not isinstance(right, UnionType):
                raise ReflectionTypeError(right, UnionType)
            return self.same_union_items(left._items, right._items)

        if isinstance(left, PartialType):
            if not isinstance(right, PartialType):
                raise ReflectionTypeError(right, PartialType)
            return (
                left._type is right._type
                and left._var is right._var
                and self.same_optional_type(left._value_type, right._value_type)
            )

        if isinstance(left, TypeType):
            if not isinstance(right, TypeType):
                raise ReflectionTypeError(right, TypeType)
            return self.same(left._item, right._item)

        if isinstance(left, PlaceholderType):
            if not isinstance(right, PlaceholderType):
                raise ReflectionTypeError(right, PlaceholderType)
            return left._fullname == right._fullname and self.same_type_lists(left._args, right._args)

        raise ReflectionTypeError(left)

    def same_type_alias_type(self, left: TypeAliasType, right: TypeAliasType) -> bool:
        if left._alias is None or right._alias is None:
            return left._alias is right._alias and self.same_type_lists(left._args, right._args)

        if left._alias is right._alias:
            return self.same_type_lists(left._args, right._args)

        if not (left.is_recursive and right.is_recursive):
            return False

        pair = (left._alias, right._alias)
        if pair in self.assumed_alias_pairs:
            return self.same_type_lists(left._args, right._args)

        self.assumed_alias_pairs.add(pair)
        try:
            return (
                self.same_type_lists(left._args, right._args) and
                self.same(left._alias._target, right._alias._target)
            )
        finally:
            self.assumed_alias_pairs.remove(pair)

    def same_expanded_aliases(self, left: Type, right: Type) -> bool:
        left_alias_type: TypeAliasType | None = left if isinstance(left, TypeAliasType) else None
        left_alias = left_alias_type._alias if left_alias_type is not None else None
        right_alias_type: TypeAliasType | None = right if isinstance(right, TypeAliasType) else None
        right_alias = right_alias_type._alias if right_alias_type is not None else None

        if left_alias is None and left_alias_type is not None:
            raise ReflectionTypeError(left)
        if right_alias is None and right_alias_type is not None:
            raise ReflectionTypeError(right)

        pair: tuple[TypeAlias, TypeAlias] | None = None
        if (
                left_alias_type is not None and
                left_alias is not None and
                right_alias_type is not None and
                right_alias is not None and
                (left_alias_type.is_recursive or right_alias_type.is_recursive)
        ):
            if not self.same_type_lists(left_alias_type._args, right_alias_type._args):
                return False
            pair = (left_alias, right_alias)
            if pair in self.assumed_alias_pairs:
                return True
            self.assumed_alias_pairs.add(pair)

        try:
            if isinstance(left, TypeAliasType):
                left = get_type_alias_target(left)
            if isinstance(right, TypeAliasType):
                right = get_type_alias_target(right)
            return self.same(left, right)
        finally:
            if pair is not None:
                self.assumed_alias_pairs.remove(pair)

    def same_type_var_id(self, left: TypeVarId, right: TypeVarId) -> bool:
        left_key = _type_var_id_key(left)
        right_key = _type_var_id_key(right)

        if not self.alpha:
            return left_key == right_key

        if (mapped_right := self.left_to_right.get(left_key)) is not None:
            return mapped_right == right_key
        if (mapped_left := self.right_to_left.get(right_key)) is not None:
            return mapped_left == left_key

        self.left_to_right[left_key] = right_key
        self.right_to_left[right_key] = left_key
        return True

    def same_optional_type(self, left: Type | None, right: Type | None) -> bool:
        if left is None or right is None:
            return left is right
        return self.same(left, right)

    def same_type_lists(self, left: ta.Sequence[Type], right: ta.Sequence[Type]) -> bool:
        return len(left) == len(right) and all(self.same(l, r) for l, r in zip(left, right))

    def same_union_items(self, left: ta.Sequence[Type], right: ta.Sequence[Type]) -> bool:
        if len(left) != len(right):
            return False

        matched = [False] * len(right)
        for left_item in left:
            found = False
            for idx, right_item in enumerate(right):
                if not matched[idx] and self.same(left_item, right_item):
                    matched[idx] = True
                    found = True
                    break
            if not found:
                return False

        return True


def _type_var_id_key(id: TypeVarId) -> tuple[str, int, int]:
    return id._namespace, id._raw_id, id._meta_level


_SUPPORTED_SAME_TYPE_NODE_TYPES: ta.Final[tuple[type[Type], ...]] = (
    TypeAliasType,
    TypeGuardedType,
    AnnotatedType,
    RequiredType,
    ReadOnlyType,
    TypeVarType,
    ParamSpecType,
    TypeVarTupleType,
    UnboundType,
    CallableArgument,
    TypeList,
    UnpackType,
    AnyType,
    UninhabitedType,
    NoneType,
    ErasedType,
    DeletedType,
    Instance,
    Parameters,
    CallableType,
    Overloaded,
    TupleType,
    TypedDictType,
    RawExpressionType,
    LiteralType,
    UnionType,
    PartialType,
    EllipsisType,
    TypeType,
    PlaceholderType,
)


def _is_supported_same_type_node(typ: Type) -> bool:
    return isinstance(typ, _SUPPORTED_SAME_TYPE_NODE_TYPES)


def _has_variadic_tuple_item(typ: TupleType) -> bool:
    return any(isinstance(item, (UnpackType, TypeVarTupleType)) for item in typ._items)


##


def is_subtype(left: Type, right: Type) -> bool:
    return _SubtypeComparer(expand_aliases=False).subtype(left, right)


def is_structural_subtype(left: Type, right: Type) -> bool:
    return _SubtypeComparer(expand_aliases=True).subtype(left, right)


class _SubtypeComparer:
    def __init__(self, *, expand_aliases: bool) -> None:
        super().__init__()

        self.expand_aliases = expand_aliases
        self.equivalence = _TypeComparer(False, expand_aliases=expand_aliases)
        self.assumed_alias_pairs: set[tuple[TypeAlias | None, TypeAlias | None]] = set()

    def subtype(self, left: Type, right: Type) -> bool:
        if self.equivalence.same(left, right):
            return True

        if isinstance(left, AnyType) or isinstance(right, AnyType):
            return True

        if isinstance(left, UninhabitedType):
            return True
        if isinstance(right, UninhabitedType):
            return False

        if isinstance(left, TypeGuardedType):
            return self.subtype(left._type_guard, right)
        if isinstance(right, TypeGuardedType):
            return self.subtype(left, right._type_guard)
        if isinstance(left, AnnotatedType):
            return self.subtype(left._item, right)
        if isinstance(right, AnnotatedType):
            return self.subtype(left, right._item)

        if self.expand_aliases and (isinstance(left, TypeAliasType) or isinstance(right, TypeAliasType)):
            return self.subtype_expanded_aliases(left, right)

        if isinstance(left, UnionType):
            return all(self.subtype(item, right) for item in left._items)
        if isinstance(right, UnionType):
            return any(self.subtype(left, item) for item in right._items)

        if isinstance(left, TypedDictType):
            return self.typed_dict_subtype(left, right)

        if isinstance(left, CallableType) and isinstance(right, CallableType):
            return self.callable_subtype(left, right)

        if isinstance(left, CallableType) and isinstance(right, Overloaded):
            return self.callable_subtype_overloaded(left, right)

        if isinstance(left, Overloaded) and isinstance(right, CallableType):
            return self.overloaded_subtype_callable(left, right)

        if isinstance(left, Overloaded) and isinstance(right, Overloaded):
            return self.overloaded_subtype(left, right)

        if isinstance(left, TupleType) and isinstance(right, TupleType):
            return self.tuple_subtype(left, right)

        if isinstance(left, TypeType) and isinstance(right, TypeType):
            return self.subtype(left._item, right._item)

        if isinstance(left, LiteralType):
            if isinstance(right, LiteralType):
                return self.equivalence.same(left, right)
            return self.subtype(left._fallback, right)

        if isinstance(right, LiteralType):
            return False

        if isinstance(left, Instance) and isinstance(right, Instance):
            return self.instance_subtype(left, right)

        raise UnsupportedTypeOperationError(f'Unsupported subtype relation: {left!r} <: {right!r}')

    def subtype_expanded_aliases(self, left: Type, right: Type) -> bool:
        left_alias_type: TypeAliasType | None = left if isinstance(left, TypeAliasType) else None
        left_alias = left_alias_type._alias if left_alias_type is not None else None
        right_alias_type: TypeAliasType | None = right if isinstance(right, TypeAliasType) else None
        right_alias = right_alias_type._alias if right_alias_type is not None else None

        if left_alias is None and isinstance(left, TypeAliasType):
            raise ReflectionTypeError(left)
        if right_alias is None and isinstance(right, TypeAliasType):
            raise ReflectionTypeError(right)

        pair: tuple[TypeAlias | None, TypeAlias | None] | None = None
        if (
                (left_alias_type is not None and left_alias is not None and left_alias_type.is_recursive) or
                (right_alias_type is not None and right_alias is not None and right_alias_type.is_recursive)
        ):
            pair = (left_alias, right_alias)
            if pair in self.assumed_alias_pairs:
                return True
            self.assumed_alias_pairs.add(pair)

        try:
            if isinstance(left, TypeAliasType):
                left = get_type_alias_target(left)
            if isinstance(right, TypeAliasType):
                right = get_type_alias_target(right)
            return self.subtype(left, right)
        finally:
            if pair is not None:
                self.assumed_alias_pairs.remove(pair)

    def overloaded_subtype(self, left: Overloaded, right: Overloaded) -> bool:
        if len(left._items) != len(right._items):
            raise UnsupportedTypeOperationError(
                f'Unsupported Overloaded subtype relation with mismatched item counts: {left!r} <: {right!r}',
            )

        return all(
            self.callable_subtype(left_item, right_item)
            for left_item, right_item in zip(left._items, right._items)
        )

    def callable_subtype_overloaded(self, left: CallableType, right: Overloaded) -> bool:
        return all(
            self.callable_subtype(left, right_item)
            for right_item in right._items
        )

    def overloaded_subtype_callable(self, left: Overloaded, right: CallableType) -> bool:
        unsupported: UnsupportedTypeOperationError | None = None
        for left_item in left._items:
            try:
                if self.callable_subtype(left_item, right):
                    return True
            except UnsupportedTypeOperationError as e:
                unsupported = e

        if unsupported is not None:
            raise UnsupportedTypeOperationError(
                f'Unsupported Overloaded subtype relation: {left!r} <: {right!r}',
            ) from unsupported

        return False

    def tuple_subtype(self, left: TupleType, right: TupleType) -> bool:
        if _has_variadic_tuple_item(left) or _has_variadic_tuple_item(right):
            raise UnsupportedTypeOperationError(f'Unsupported variadic Tuple subtype relation: {left!r} <: {right!r}')

        if len(left._items) != len(right._items):
            return False

        return all(
            self.subtype(left_item, right_item)
            for left_item, right_item in zip(left._items, right._items)
        )

    def callable_subtype(self, left: CallableType, right: CallableType) -> bool:
        if left._variables or right._variables:
            raise UnsupportedTypeOperationError(f'Unsupported generic Callable subtype relation: {left!r} <: {right!r}')

        if not _has_callable_arg_metadata_shape(left) or not _has_callable_arg_metadata_shape(right):
            raise UnsupportedTypeOperationError(
                f'Unsupported malformed Callable subtype relation: {left!r} <: {right!r}',
            )

        if not self.subtype(left._ret_type, right._ret_type):
            return False

        if left._is_ellipsis_args:
            return right._is_ellipsis_args

        if right._is_ellipsis_args:
            return False

        return _are_callable_args_compatible(left, right, self.subtype)

    def typed_dict_subtype(self, left: TypedDictType, right: Type) -> bool:
        if isinstance(right, Instance):
            return self.instance_subtype(left._fallback, right)

        if not isinstance(right, TypedDictType):
            return False

        for name, right_item in right._items.items():
            if name not in left._items:
                if name in right._required_keys:
                    return False
                continue

            left_item = left._items[name]
            right_readonly = name in right._readonly_keys

            if right_readonly:
                if not self.subtype(left_item, right_item):
                    return False
            elif not self.equivalence.same(left_item, right_item):
                return False

            left_required = name in left._required_keys
            right_required = name in right._required_keys
            if right_required and not left_required:
                return False
            if left_required and not right_required and not right_readonly:
                return False

            if name in left._readonly_keys and not right_readonly:
                return False

        return True

    def instance_subtype(self, left: Instance, right: Instance) -> bool:
        if left._type is right._type:
            return self.same_instance_type_subtype(left, right)

        if right._type not in left._type._mro:
            return False

        if right._args:
            mapped = get_base_instance(left, right._type)
            if mapped is not None and len(mapped._args) == len(right._args):
                return self.same_instance_type_subtype(mapped, right)
            raise UnsupportedTypeOperationError(
                f'Generic base instance mapping is not implemented: {left!r} <: {right!r}',
            )

        return True

    def same_instance_type_subtype(self, left: Instance, right: Instance) -> bool:
        if len(left._args) != len(right._args):
            return False

        for index, (left_arg, right_arg) in enumerate(zip(left._args, right._args)):
            variance = VarianceKind.IN
            if index < len(left._type._variances):
                variance = left._type._variances[index]

            if variance is VarianceKind.CO:
                if not self.subtype(left_arg, right_arg):
                    return False
            elif variance is VarianceKind.CONTRA:
                if not self.subtype(right_arg, left_arg):
                    return False
            else:
                if not self.equivalence.same(left_arg, right_arg):
                    return False

        return True


def _is_subtype_legacy(left: Type, right: Type) -> bool:
    if is_same_type(left, right):
        return True

    if isinstance(left, AnyType) or isinstance(right, AnyType):
        return True

    if isinstance(left, UninhabitedType):
        return True
    if isinstance(right, UninhabitedType):
        return False

    if isinstance(left, TypeGuardedType):
        return is_subtype(left._type_guard, right)
    if isinstance(right, TypeGuardedType):
        return is_subtype(left, right._type_guard)
    if isinstance(left, AnnotatedType):
        return is_subtype(left._item, right)
    if isinstance(right, AnnotatedType):
        return is_subtype(left, right._item)

    if isinstance(left, UnionType):
        return all(is_subtype(item, right) for item in left._items)
    if isinstance(right, UnionType):
        return any(is_subtype(left, item) for item in right._items)

    if isinstance(left, TypedDictType):
        return _is_typed_dict_subtype(left, right)

    if isinstance(left, CallableType) and isinstance(right, CallableType):
        return _is_callable_subtype(left, right)

    if isinstance(left, TypeType) and isinstance(right, TypeType):
        return is_subtype(left._item, right._item)

    if isinstance(left, Instance) and isinstance(right, Instance):
        return _is_instance_subtype(left, right)

    raise UnsupportedTypeOperationError(f'Unsupported subtype relation: {left!r} <: {right!r}')


def _is_callable_subtype(left: CallableType, right: CallableType) -> bool:
    if left._variables or right._variables:
        raise UnsupportedTypeOperationError(f'Unsupported generic Callable subtype relation: {left!r} <: {right!r}')

    if not _has_callable_arg_metadata_shape(left) or not _has_callable_arg_metadata_shape(right):
        raise UnsupportedTypeOperationError(f'Unsupported malformed Callable subtype relation: {left!r} <: {right!r}')

    if not is_subtype(left._ret_type, right._ret_type):
        return False

    if left._is_ellipsis_args:
        return right._is_ellipsis_args

    if right._is_ellipsis_args:
        return False

    return _are_callable_args_compatible(left, right, is_subtype)


def _is_required_arg_kind(kind: object) -> bool:
    return kind is ArgKind.POS or kind is ArgKind.NAMED


def _is_star_arg_kind(kind: object) -> bool:
    return kind is ArgKind.STAR or kind is ArgKind.STAR2


def _is_positional_arg_kind(kind: object) -> bool:
    return kind is ArgKind.POS or kind is ArgKind.OPT


def _is_named_arg_kind(kind: object) -> bool:
    return kind is ArgKind.NAMED or kind is ArgKind.NAMED_OPT


def _has_callable_arg_metadata_shape(typ: CallableType) -> bool:
    return len(typ._arg_types) == len(typ._arg_kinds) == len(typ._arg_names)


def _callable_arg_matches(
        left_kind: object,
        left_name: str | None,
        right_kind: object,
        right_name: str | None,
) -> bool:
    if _is_positional_arg_kind(right_kind):
        return _is_positional_arg_kind(left_kind) and left_name == right_name

    if _is_named_arg_kind(right_kind):
        return _is_named_arg_kind(left_kind) and left_name == right_name

    return left_kind is right_kind and left_name == right_name


def _are_callable_args_compatible(
        left: CallableType,
        right: CallableType,
        is_compat: ta.Callable[[Type, Type], bool],
) -> bool:
    if any(_is_star_arg_kind(kind) for kind in left._arg_kinds + right._arg_kinds):
        return (
            left._arg_kinds == right._arg_kinds
            and left._arg_names == right._arg_names
            and len(left._arg_types) == len(right._arg_types)
            and all(
                is_compat(right_arg, left_arg)
                for left_arg, right_arg in zip(left._arg_types, right._arg_types)
            )
        )

    left_used: set[int] = set()
    for right_index, right_arg in enumerate(right._arg_types):
        right_kind = right._arg_kinds[right_index]
        right_name = right._arg_names[right_index]

        match_index: int | None = None
        for left_index, left_arg in enumerate(left._arg_types):
            if left_index in left_used:
                continue
            if not _callable_arg_matches(
                    left._arg_kinds[left_index],
                    left._arg_names[left_index],
                    right_kind,
                    right_name,
            ):
                continue
            if not is_compat(right_arg, left_arg):
                return False
            match_index = left_index
            break

        if match_index is None:
            return False
        left_used.add(match_index)

    for left_index, left_kind in enumerate(left._arg_kinds):
        if left_index not in left_used and _is_required_arg_kind(left_kind):
            return False

    return True


def _is_typed_dict_subtype(left: TypedDictType, right: Type) -> bool:
    if isinstance(right, Instance):
        return _is_instance_subtype(left._fallback, right)

    if not isinstance(right, TypedDictType):
        return False

    for name, right_item in right._items.items():
        if name not in left._items:
            if name in right._required_keys:
                return False
            continue

        left_item = left._items[name]
        right_readonly = name in right._readonly_keys

        if right_readonly:
            if not is_subtype(left_item, right_item):
                return False
        elif not is_same_type(left_item, right_item):
            return False

        left_required = name in left._required_keys
        right_required = name in right._required_keys
        if right_required and not left_required:
            return False
        if left_required and not right_required and not right_readonly:
            return False

        if name in left._readonly_keys and not right_readonly:
            return False

    return True


def _is_instance_subtype(left: Instance, right: Instance) -> bool:
    if left._type is right._type:
        return _is_same_instance_type_subtype(left, right)

    if right._type not in left._type._mro:
        return False

    if right._args:
        mapped = get_base_instance(left, right._type)
        if mapped is not None and len(mapped._args) == len(right._args):
            return _is_same_instance_type_subtype(mapped, right)
        raise UnsupportedTypeOperationError(f'Generic base instance mapping is not implemented: {left!r} <: {right!r}')

    return True


def _is_same_instance_type_subtype(left: Instance, right: Instance) -> bool:
    if len(left._args) != len(right._args):
        return False

    for index, (left_arg, right_arg) in enumerate(zip(left._args, right._args)):
        variance = VarianceKind.IN
        if index < len(left._type._variances):
            variance = left._type._variances[index]

        if variance is VarianceKind.CO:
            if not is_subtype(left_arg, right_arg):
                return False
        elif variance is VarianceKind.CONTRA:
            if not is_subtype(right_arg, left_arg):
                return False
        else:
            if not is_same_type(left_arg, right_arg):
                return False

    return True


def is_subtype_or_false(left: Type, right: Type) -> bool:
    try:
        return is_subtype(left, right)
    except UnsupportedTypeOperationError:
        return False
