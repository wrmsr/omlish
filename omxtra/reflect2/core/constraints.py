# ruff: noqa: SLF001
import enum
import typing as ta

from ..errors import ReflectionError
from ..errors import ReflectionValueError
from ..errors import UnsupportedTypeOperationError
from .subtypes import get_base_instance
from .subtypes import is_same_type
from .subtypes import is_structurally_equivalent
from .symbols import ArgKind
from .symbols import TypeAlias
from .symbols import VarianceKind
from .typeops import get_type_alias_target
from .typeops import has_type_vars
from .types import AnnotatedType
from .types import AnyType
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
from .types import PlaceholderType
from .types import RawExpressionType
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
from .types import UninhabitedType
from .types import UnionType
from .types import UnpackType


##


class ConstraintOp(enum.Enum):
    SUBTYPE_OF = 0
    SUPERTYPE_OF = 1


class Constraint:
    __slots__ = (
        '_type_var',
        '_op',
        '_target',
        '_origin_type_var',
    )

    def __init__(
            self,
            type_var: TypeVarLikeType,
            op: ConstraintOp,
            target: Type,
    ) -> None:
        super().__init__()

        self._type_var = type_var._id
        self._op = op
        self._target = target
        self._origin_type_var = type_var

    @property
    def type_var(self) -> TypeVarId:
        return self._type_var

    @property
    def op(self) -> ConstraintOp:
        return self._op

    @property
    def target(self) -> Type:
        return self._target

    @property
    def origin_type_var(self) -> TypeVarLikeType:
        return self._origin_type_var

    def __repr__(self) -> str:
        op_str = '<:' if self._op is ConstraintOp.SUBTYPE_OF else ':>'
        return f'{self._type_var!r} {op_str} {self._target!r}'


##


def neg_op(op: ConstraintOp) -> ConstraintOp:
    if op == ConstraintOp.SUBTYPE_OF:
        return ConstraintOp.SUPERTYPE_OF
    if op == ConstraintOp.SUPERTYPE_OF:
        return ConstraintOp.SUBTYPE_OF
    raise ReflectionValueError(op)


def infer_constraints(
        template: Type,
        actual: Type,
        direction: ConstraintOp,
) -> list[Constraint]:
    if direction not in (ConstraintOp.SUBTYPE_OF, ConstraintOp.SUPERTYPE_OF):
        raise ReflectionValueError(direction)

    return _ConstraintInferrer(direction).infer(template, actual)


class _ConstraintInferrer:
    def __init__(
            self,
            direction: ConstraintOp,
            assumed_alias_pairs: set[tuple[TypeAlias | None, TypeAlias | None]] | None = None,
    ) -> None:
        super().__init__()

        self._direction = direction
        self._assumed_alias_pairs = set() if assumed_alias_pairs is None else assumed_alias_pairs

    def infer(self, template: Type, actual: Type) -> list[Constraint]:
        if isinstance(template, TypeVarType):
            return [Constraint(template, self._direction, actual)]
        if isinstance(template, ParamSpecType):
            if isinstance(actual, (Parameters, ParamSpecType)):
                return [Constraint(template, self._direction, actual)]
            raise UnsupportedTypeOperationError(
                f'Unsupported ParamSpec constraint inference: {template!r} ~ {actual!r}',
            )
        if isinstance(template, TypeVarTupleType):
            if isinstance(actual, (TupleType, TypeList, TypeVarTupleType)):
                return [Constraint(template, self._direction, actual)]
            raise UnsupportedTypeOperationError(
                f'Unsupported TypeVarTuple constraint inference: {template!r} ~ {actual!r}',
            )

        if isinstance(template, AnyType) or isinstance(actual, AnyType):
            return []

        if isinstance(template, TypeAliasType) or isinstance(actual, TypeAliasType):
            return self.infer_aliases(template, actual)

        if isinstance(template, AnnotatedType):
            return self.infer(template._item, actual)
        if isinstance(actual, AnnotatedType):
            return self.infer(template, actual._item)
        if isinstance(template, TypeGuardedType):
            return self.infer(template._type_guard, actual)
        if isinstance(actual, TypeGuardedType):
            return self.infer(template, actual._type_guard)

        if isinstance(template, TypeType) and isinstance(actual, TypeType):
            return self.infer(template._item, actual._item)

        if isinstance(template, UnionType) and isinstance(actual, UnionType):
            return self.infer_unions(template, actual)

        if isinstance(template, TupleType) and isinstance(actual, TupleType):
            return self.infer_tuples(template, actual)

        if isinstance(template, TypedDictType) and isinstance(actual, TypedDictType):
            return self.infer_typed_dicts(template, actual)

        if isinstance(template, Instance) and isinstance(actual, Instance):
            return self.infer_instances(template, actual)

        if isinstance(template, Overloaded) and isinstance(actual, CallableType):
            return self.infer_overloaded(template, actual)

        if isinstance(template, Overloaded) and isinstance(actual, Overloaded):
            return self.infer_overloaded_from_overloaded(template, actual)

        if isinstance(template, CallableType) and isinstance(actual, Overloaded):
            return self.infer_callable_from_overloaded(template, actual)

        if isinstance(template, CallableType) and isinstance(actual, CallableType):
            return self.infer_callables(template, actual)

        if _is_concrete_constraint_leaf(template) and _is_concrete_constraint_leaf(actual):
            if _is_same_constraint_type(template, actual):
                return []
            raise UnsupportedTypeOperationError(
                f'Unsupported concrete leaf constraint inference: {template!r} ~ {actual!r}',
            )

        raise UnsupportedTypeOperationError(f'Unsupported constraint inference: {template!r} ~ {actual!r}')

    def infer_instances(self, template: Instance, actual: Instance) -> list[Constraint]:
        if template._type is not actual._type:
            mapped = get_base_instance(actual, template._type)
            if mapped is None:
                if _is_concrete_constraint_leaf(template) and _is_concrete_constraint_leaf(actual):
                    return []
                raise UnsupportedTypeOperationError(
                    f'Unsupported instance constraint inference: {template!r} ~ {actual!r}',
                )
            actual = mapped

        if len(template._args) != len(actual._args):
            raise UnsupportedTypeOperationError(
                f'Unsupported instance constraint inference with mismatched args: {template!r} ~ {actual!r}',
            )

        constraints: list[Constraint] = []
        for index, (template_arg, actual_arg) in enumerate(zip(template._args, actual._args)):
            variance = VarianceKind.IN
            if index < len(template._type._variances):
                variance = template._type._variances[index]

            if variance is VarianceKind.CO:
                constraints.extend(self.infer(template_arg, actual_arg))
            elif variance is VarianceKind.CONTRA:
                constraints.extend(self.infer_with_direction(template_arg, actual_arg, neg_op(self._direction)))
            elif variance is VarianceKind.IN:
                constraints.extend(self.infer(template_arg, actual_arg))
                constraints.extend(self.infer_with_direction(template_arg, actual_arg, neg_op(self._direction)))
            else:
                raise UnsupportedTypeOperationError(
                    f'Unsupported variance in constraint inference: {template._type._fullname}',
                )

        return constraints

    def infer_unions(self, template: UnionType, actual: UnionType) -> list[Constraint]:
        if len(template._items) != len(actual._items):
            raise UnsupportedTypeOperationError(
                f'Unsupported Union constraint inference with mismatched items: {template!r} ~ {actual!r}',
            )

        remaining_actual = list(actual._items)
        delayed_template: list[Type] = []

        for template_item in template._items:
            if has_type_vars(template_item):
                delayed_template.append(template_item)
                continue

            match_indexes = [
                index
                for index, actual_item in enumerate(remaining_actual)
                if _is_same_constraint_type(template_item, actual_item)
            ]
            if len(match_indexes) != 1:
                raise UnsupportedTypeOperationError(
                    f'Unsupported Union constraint inference with unmatched concrete item: {template!r} ~ {actual!r}',
                )
            del remaining_actual[match_indexes[0]]

        constraints: list[Constraint] = []
        for template_item in delayed_template:
            matches: list[tuple[int, list[Constraint]]] = []
            for index, actual_item in enumerate(remaining_actual):
                try:
                    item_constraints = self.infer(template_item, actual_item)
                except UnsupportedTypeOperationError:
                    continue

                matches.append((index, item_constraints))

            if len(matches) != 1:
                raise UnsupportedTypeOperationError(
                    f'Unsupported ambiguous Union constraint inference: {template!r} ~ {actual!r}',
                )

            match_index, item_constraints = matches[0]
            constraints.extend(item_constraints)
            del remaining_actual[match_index]

        if remaining_actual:
            raise UnsupportedTypeOperationError(
                f'Unsupported Union constraint inference with unmatched actual items: {template!r} ~ {actual!r}',
            )

        return constraints

    def infer_tuples(self, template: TupleType, actual: TupleType) -> list[Constraint]:
        if any(isinstance(item, (UnpackType, TypeVarTupleType)) for item in actual._items):
            raise UnsupportedTypeOperationError(
                f'Unsupported variadic Tuple constraint inference: {template!r} ~ {actual!r}',
            )

        if not is_same_type(template._partial_fallback, actual._partial_fallback):
            raise UnsupportedTypeOperationError(
                f'Unsupported Tuple constraint inference with mismatched fallbacks: {template!r} ~ {actual!r}',
            )

        variadic_index = _get_tuple_variadic_index(template)
        if variadic_index is None:
            if len(template._items) != len(actual._items):
                raise UnsupportedTypeOperationError(
                    f'Unsupported Tuple constraint inference with mismatched items: {template!r} ~ {actual!r}',
                )
        else:
            return self.infer_variadic_tuple(template, actual, variadic_index)

        constraints: list[Constraint] = []
        for template_item, actual_item in zip(template._items, actual._items):
            constraints.extend(self.infer(template_item, actual_item))

        return constraints

    def infer_variadic_tuple(
            self,
            template: TupleType,
            actual: TupleType,
            variadic_index: int,
    ) -> list[Constraint]:
        prefix_len = variadic_index
        suffix_len = len(template._items) - variadic_index - 1
        if len(actual._items) < prefix_len + suffix_len:
            raise UnsupportedTypeOperationError(
                f'Unsupported Tuple constraint inference with mismatched items: {template!r} ~ {actual!r}',
            )

        constraints: list[Constraint] = []
        for template_item, actual_item in zip(template._items[:prefix_len], actual._items[:prefix_len]):
            constraints.extend(self.infer(template_item, actual_item))

        if suffix_len:
            template_suffix = template._items[-suffix_len:]
            actual_suffix = actual._items[-suffix_len:]
            for template_item, actual_item in zip(template_suffix, actual_suffix):
                constraints.extend(self.infer(template_item, actual_item))

        type_var_tuple = _get_type_var_tuple_item(template._items[variadic_index])
        if type_var_tuple is None:
            raise UnsupportedTypeOperationError(
                f'Unsupported variadic Tuple constraint inference: {template!r} ~ {actual!r}',
            )

        capture_start = prefix_len
        capture_end = len(actual._items) - suffix_len
        constraints.extend(self.infer(
            type_var_tuple,
            TupleType(list(actual._items[capture_start:capture_end]), actual._partial_fallback),
        ))

        return constraints

    def infer_typed_dicts(self, template: TypedDictType, actual: TypedDictType) -> list[Constraint]:
        if template._items.keys() != actual._items.keys():
            raise UnsupportedTypeOperationError(
                f'Unsupported TypedDict constraint inference with mismatched keys: {template!r} ~ {actual!r}',
            )

        if template._required_keys != actual._required_keys:
            raise UnsupportedTypeOperationError(
                f'Unsupported TypedDict constraint inference with mismatched required keys: {template!r} ~ {actual!r}',
            )

        if template._readonly_keys != actual._readonly_keys:
            raise UnsupportedTypeOperationError(
                f'Unsupported TypedDict constraint inference with mismatched readonly keys: {template!r} ~ {actual!r}',
            )

        if not is_same_type(template._fallback, actual._fallback):
            raise UnsupportedTypeOperationError(
                f'Unsupported TypedDict constraint inference with mismatched fallbacks: {template!r} ~ {actual!r}',
            )

        constraints: list[Constraint] = []
        for name in sorted(template._items):
            template_item = template._items[name]
            actual_item = actual._items[name]
            constraints.extend(self.infer(template_item, actual_item))
            if name not in template._readonly_keys:
                constraints.extend(self.infer_with_direction(template_item, actual_item, neg_op(self._direction)))

        return constraints

    def infer_overloaded(self, template: Overloaded, actual: CallableType) -> list[Constraint]:
        matches: list[list[Constraint]] = []
        for item in template._items:
            try:
                matches.append(self.infer_callables(item, actual))
            except UnsupportedTypeOperationError:
                pass

        if len(matches) != 1:
            raise UnsupportedTypeOperationError(
                f'Unsupported Overloaded constraint inference with {len(matches)} matches: {template!r} ~ {actual!r}',
            )

        return matches[0]

    def infer_callable_from_overloaded(self, template: CallableType, actual: Overloaded) -> list[Constraint]:
        constraints: list[Constraint] = []
        for item in actual._items:
            constraints.extend(self.infer_callables(template, item))
        return constraints

    def infer_overloaded_from_overloaded(self, template: Overloaded, actual: Overloaded) -> list[Constraint]:
        if len(template._items) != len(actual._items):
            raise UnsupportedTypeOperationError(
                f'Unsupported Overloaded constraint inference with mismatched item counts: {template!r} ~ {actual!r}',
            )

        constraints: list[Constraint] = []
        for template_item, actual_item in zip(template._items, actual._items):
            constraints.extend(self.infer_callables(template_item, actual_item))
        return constraints

    def infer_callables(self, template: CallableType, actual: CallableType) -> list[Constraint]:
        param_spec_template = _get_param_spec_arg_template(template)
        if param_spec_template is not None:
            param_spec, prefix_len = param_spec_template
            if actual._variables:
                raise UnsupportedTypeOperationError(
                    f'Unsupported generic Callable constraint inference: {template!r} ~ {actual!r}',
                )
            if actual._is_ellipsis_args:
                raise UnsupportedTypeOperationError(
                    f'Unsupported ellipsis Callable constraint inference: {template!r} ~ {actual!r}',
                )
            if not is_same_type(template._fallback, actual._fallback):
                raise UnsupportedTypeOperationError(
                    f'Unsupported Callable constraint inference with mismatched fallbacks: {template!r} ~ {actual!r}',
                )
            if len(actual._arg_types) < prefix_len:
                raise UnsupportedTypeOperationError(
                    f'Unsupported Callable constraint inference with mismatched args: {template!r} ~ {actual!r}',
                )

            constraints = self.infer(template._ret_type, actual._ret_type)

            for index in range(prefix_len):
                if (
                        template._arg_kinds[index] is not actual._arg_kinds[index] or
                        template._arg_names[index] != actual._arg_names[index]
                ):
                    raise UnsupportedTypeOperationError(
                        f'Unsupported Callable constraint inference with mismatched args: {template!r} ~ {actual!r}',
                    )
                constraints.extend(self.infer_with_direction(
                    template._arg_types[index],
                    actual._arg_types[index],
                    neg_op(self._direction),
                ))

            constraints.extend(self.infer_with_direction(
                param_spec,
                Parameters(
                    list(actual._arg_types[prefix_len:]),
                    list(actual._arg_kinds[prefix_len:]),
                    list(actual._arg_names[prefix_len:]),
                ),
                neg_op(self._direction),
            ))
            return constraints

        if template._variables or actual._variables:
            raise UnsupportedTypeOperationError(
                f'Unsupported generic Callable constraint inference: {template!r} ~ {actual!r}',
            )

        if template._is_ellipsis_args or actual._is_ellipsis_args:
            raise UnsupportedTypeOperationError(
                f'Unsupported ellipsis Callable constraint inference: {template!r} ~ {actual!r}',
            )

        if not _has_same_callable_arg_shape(template, actual):
            raise UnsupportedTypeOperationError(
                f'Unsupported Callable constraint inference with mismatched args: {template!r} ~ {actual!r}',
            )

        if not is_same_type(template._fallback, actual._fallback):
            raise UnsupportedTypeOperationError(
                f'Unsupported Callable constraint inference with mismatched fallbacks: {template!r} ~ {actual!r}',
            )

        constraints = self.infer(template._ret_type, actual._ret_type)
        for template_arg, actual_arg in zip(template._arg_types, actual._arg_types):
            constraints.extend(self.infer_with_direction(template_arg, actual_arg, neg_op(self._direction)))

        return constraints

    def infer_with_direction(self, template: Type, actual: Type, direction: ConstraintOp) -> list[Constraint]:
        if direction is self._direction:
            return self.infer(template, actual)
        return _ConstraintInferrer(direction, self._assumed_alias_pairs).infer(template, actual)

    def infer_type_lists(self, templates: ta.Sequence[Type], actuals: ta.Sequence[Type]) -> list[Constraint]:
        if len(templates) != len(actuals):
            raise UnsupportedTypeOperationError(
                f'Unsupported alias constraint inference with mismatched args: {templates!r} ~ {actuals!r}',
            )

        constraints: list[Constraint] = []
        for template, actual in zip(templates, actuals):
            constraints.extend(self.infer(template, actual))
        return constraints

    def infer_aliases(self, template: Type, actual: Type) -> list[Constraint]:
        template_alias_type = template if isinstance(template, TypeAliasType) else None
        template_alias = template_alias_type._alias if template_alias_type is not None else None
        actual_alias_type = actual if isinstance(actual, TypeAliasType) else None
        actual_alias = actual_alias_type._alias if actual_alias_type is not None else None

        if template_alias is None and template_alias_type is not None:
            raise UnsupportedTypeOperationError(f'Unsupported unfixed alias in constraint inference: {template!r}')
        if actual_alias is None and actual_alias_type is not None:
            raise UnsupportedTypeOperationError(f'Unsupported unfixed alias in constraint inference: {actual!r}')

        template_recursive = template_alias_type is not None and template_alias_type.is_recursive
        actual_recursive = actual_alias_type is not None and actual_alias_type.is_recursive
        if not (template_recursive or actual_recursive):
            if template_alias_type is not None:
                template = _expand_constraint_alias(template_alias_type, allow_recursive=False)
            if actual_alias_type is not None:
                actual = _expand_constraint_alias(actual_alias_type, allow_recursive=False)
            return self.infer(template, actual)

        pair = (template_alias, actual_alias)
        if pair in self._assumed_alias_pairs:
            if template_alias_type is not None and actual_alias_type is not None:
                return self.infer_type_lists(template_alias_type._args, actual_alias_type._args)
            return []

        self._assumed_alias_pairs.add(pair)
        try:
            if template_alias_type is not None:
                template = _expand_constraint_alias(template_alias_type, allow_recursive=True)
            if actual_alias_type is not None:
                actual = _expand_constraint_alias(actual_alias_type, allow_recursive=True)
            return self.infer(template, actual)
        finally:
            self._assumed_alias_pairs.remove(pair)


_CONCRETE_CONSTRAINT_LEAF_TYPES: ta.Final[tuple[type[Type], ...]] = (
    UninhabitedType,
    NoneType,
    ErasedType,
    DeletedType,
    RawExpressionType,
    LiteralType,
    EllipsisType,
    PlaceholderType,
)


def _is_concrete_constraint_leaf(typ: Type) -> bool:
    return isinstance(typ, _CONCRETE_CONSTRAINT_LEAF_TYPES)


def _is_same_constraint_type(left: Type, right: Type) -> bool:
    if is_same_type(left, right):
        return True

    try:
        return is_structurally_equivalent(left, right)
    except ReflectionError:
        return False


def _get_type_var_tuple_item(typ: Type) -> TypeVarTupleType | None:
    if isinstance(typ, TypeVarTupleType):
        return typ
    if isinstance(typ, UnpackType) and isinstance(typ._type, TypeVarTupleType):
        return typ._type
    return None


def _get_tuple_variadic_index(typ: TupleType) -> int | None:
    variadic_index = -1
    for index, item in enumerate(typ._items):
        if isinstance(item, (UnpackType, TypeVarTupleType)):
            if _get_type_var_tuple_item(item) is None:
                raise UnsupportedTypeOperationError(f'Unsupported variadic Tuple constraint inference: {typ!r}')
            if variadic_index >= 0:
                raise UnsupportedTypeOperationError(f'Unsupported variadic Tuple constraint inference: {typ!r}')
            variadic_index = index

    if variadic_index < 0:
        return None
    return variadic_index


def _get_param_spec_arg_template(typ: CallableType) -> tuple[ParamSpecType, int] | None:
    if len(typ._variables) != 1:
        return None
    var = typ._variables[0]
    if not isinstance(var, ParamSpecType):
        return None
    if len(typ._arg_types) < 2:
        return None
    prefix_len = len(typ._arg_types) - 2
    for arg_type in typ._arg_types[prefix_len:]:
        if not isinstance(arg_type, ParamSpecType):
            return None
        if not _is_same_type_var_id(arg_type._id, var._id):
            return None
    if typ._arg_kinds[prefix_len:] != [ArgKind.STAR, ArgKind.STAR2]:
        return None
    if typ._arg_names[prefix_len:] != [None, None]:
        return None
    if any(kind in (ArgKind.STAR, ArgKind.STAR2) for kind in typ._arg_kinds[:prefix_len]):
        return None
    return var, prefix_len


def _is_same_type_var_id(left: TypeVarId, right: TypeVarId) -> bool:
    return (
        left._namespace == right._namespace
        and left._raw_id == right._raw_id
        and left._meta_level == right._meta_level
    )


def _expand_constraint_alias(typ: TypeAliasType, *, allow_recursive: bool) -> Type:
    if typ._alias is None:
        raise UnsupportedTypeOperationError(f'Unsupported unfixed alias in constraint inference: {typ!r}')

    if typ.is_recursive and not allow_recursive:
        raise UnsupportedTypeOperationError(f'Unsupported recursive alias in constraint inference: {typ!r}')

    try:
        return get_type_alias_target(typ)
    except ReflectionError as e:
        raise UnsupportedTypeOperationError(f'Unsupported alias in constraint inference: {typ!r}') from e


def _has_same_callable_arg_shape(left: CallableType, right: CallableType) -> bool:
    if len(left._arg_types) != len(right._arg_types):
        return False

    return left._arg_kinds == right._arg_kinds and left._arg_names == right._arg_names
