# ruff: noqa: SLF001
import typing as ta

from ..errors import ReflectionTypeError
from .constraints import Constraint
from .constraints import ConstraintOp
from .join import join_type_list
from .join import structural_join_type_list
from .meet import meet_type_list
from .meet import structural_meet_type_list
from .subtypes import is_same_type
from .subtypes import is_structural_subtype
from .subtypes import is_subtype
from .types import _ANY_TYPES
from .types import _UNINHABITED_TYPE
from .types import Parameters
from .types import ParamSpecType
from .types import TupleType
from .types import Type
from .types import TypeList
from .types import TypeOfAny
from .types import TypeVarId
from .types import TypeVarLikeType
from .types import TypeVarTupleType
from .types import TypeVarType


##


def solve_constraints(
        original_vars: ta.Sequence[TypeVarLikeType],
        constraints: list[Constraint],
        *,
        strict: bool = True,
) -> list[Type | None]:
    if not original_vars:
        return []

    var_ids = [var._id for var in original_vars]
    constraints_by_var: dict[TypeVarId, list[Constraint]] = {var_id: [] for var_id in var_ids}
    for constraint in constraints:
        if constraint._type_var in constraints_by_var:
            constraints_by_var[constraint._type_var].append(constraint)

    return [
        _solve_one_var(var, constraints_by_var[var._id], strict)
        for var in original_vars
    ]


def _solve_one_var(
        var: TypeVarLikeType,
        constraints: list[Constraint],
        strict: bool,
) -> Type | None:
    if not constraints:
        if strict:
            return _UNINHABITED_TYPE
        return _ANY_TYPES[TypeOfAny.SPECIAL_FORM]

    lowers = [constraint._target for constraint in constraints if constraint._op is ConstraintOp.SUPERTYPE_OF]
    uppers = [constraint._target for constraint in constraints if constraint._op is ConstraintOp.SUBTYPE_OF]

    if isinstance(var, ParamSpecType):
        return _solve_packed_var(
            lowers,
            uppers,
            (Parameters, ParamSpecType),
        )
    if isinstance(var, TypeVarTupleType):
        return _solve_packed_var(
            lowers,
            uppers,
            (TupleType, TypeList, TypeVarTupleType),
        )

    solution = solve_one(lowers, uppers)

    if solution is None:
        return None

    if isinstance(var, TypeVarType):
        return _validate_type_var_solution(var, solution)

    return solution


def solve_one(
        lowers: ta.Iterable[Type],
        uppers: ta.Iterable[Type],
) -> Type | None:
    lower_list = list(lowers)
    upper_list = list(uppers)

    if not lower_list and not upper_list:
        return None

    bottom = _join_solution_types(lower_list) if lower_list else None
    top = _meet_solution_types(upper_list) if upper_list else None

    if bottom is None:
        return top
    if top is None:
        return bottom

    if _is_solution_subtype(bottom, top):
        return bottom

    return None


def _join_solution_types(items: list[Type]) -> Type:
    try:
        return join_type_list(items)
    except ReflectionTypeError:
        return structural_join_type_list(items)


def _meet_solution_types(items: list[Type]) -> Type:
    try:
        return meet_type_list(items)
    except ReflectionTypeError:
        return structural_meet_type_list(items)


def _is_solution_subtype(left: Type, right: Type) -> bool:
    try:
        return is_subtype(left, right)
    except ReflectionTypeError:
        return is_structural_subtype(left, right)


def _validate_type_var_solution(var: TypeVarType, solution: Type) -> Type | None:
    if var._values:
        for value in var._values:
            if is_subtype(solution, value):
                return value
        return None

    try:
        if not _is_solution_subtype(solution, var._upper_bound):
            return None
    except ReflectionTypeError:
        return None

    return solution


def _solve_packed_var(
        lowers: ta.Sequence[Type],
        uppers: ta.Sequence[Type],
        allowed_types: tuple[type[Type], ...],
) -> Type | None:
    candidates = [*lowers, *uppers]
    if not candidates:
        return None

    first = candidates[0]
    if not isinstance(first, allowed_types):
        return None

    for candidate in candidates[1:]:
        if not isinstance(candidate, allowed_types):
            return None
        if not is_same_type(first, candidate):
            return None

    return first
