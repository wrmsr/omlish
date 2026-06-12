# ruff: noqa: F821 PLC0132 SLF001
# ruff: noqa: PYI059
import collections.abc as cabc
import typing as ta

import pytest

from ..core import symbols
from ..core import types
from ..core.constraints import ConstraintOp
from ..core.constraints import infer_constraints
from ..core.solve import solve_constraints
from ..core.strconv import type_str
from ..core.substitute import substitute_type
from ..core.typeops import get_proper_type
from ..errors import ReflectionError
from ..errors import UnreflectableTypeError
from ..errors import UnsupportedTypeOperationError
from ..ops import reflect_alpha_structural_type_key
from ..ops import reflect_alpha_structural_type_key_or_none
from ..ops import reflect_alpha_type_key
from ..ops import reflect_alpha_type_key_or_none
from ..ops import reflect_base_args
from ..ops import reflect_base_args_or_none
from ..ops import reflect_base_instance
from ..ops import reflect_base_instance_or_none
from ..ops import reflect_instance
from ..ops import reflect_instance_args
from ..ops import reflect_instance_info
from ..ops import reflect_is_alpha_equivalent
from ..ops import reflect_is_alpha_structurally_equivalent
from ..ops import reflect_is_alpha_structurally_equivalent_or_false
from ..ops import reflect_is_assignable
from ..ops import reflect_is_assignable_or_false
from ..ops import reflect_is_same_type
from ..ops import reflect_is_structural_subtype
from ..ops import reflect_is_structural_subtype_or_false
from ..ops import reflect_is_structurally_equivalent
from ..ops import reflect_is_structurally_equivalent_or_false
from ..ops import reflect_join
from ..ops import reflect_join_list
from ..ops import reflect_literal_values
from ..ops import reflect_literal_values_or_none
from ..ops import reflect_meet
from ..ops import reflect_meet_list
from ..ops import reflect_mro_entries
from ..ops import reflect_mro_entries_or_none
from ..ops import reflect_mro_instances
from ..ops import reflect_mro_instances_or_none
from ..ops import reflect_mro_type_strs
from ..ops import reflect_structural_join
from ..ops import reflect_structural_join_list
from ..ops import reflect_structural_meet
from ..ops import reflect_structural_meet_list
from ..ops import reflect_structural_type_key
from ..ops import reflect_structural_type_key_or_none
from ..ops import reflect_substitute_type
from ..ops import reflect_substitute_types
from ..ops import reflect_type_key
from ..ops import reflect_type_key_or_none
from ..ops import reflect_type_str
from ..ops import reflect_type_strs
from ..ops import reflect_typed_dict_literal_values
from ..queries import reflect_runtime_effective_type_key
from ..reflect import RuntimeTypeReflector
from ..universe import DYNAMIC_TYPE_NAME_COUNTER
from ..universe import RuntimeTypeUniverse


def test_reflect_join_returns_matching_runtime_generic_base() -> None:
    t_var = ta.TypeVar('T')  # type: ignore

    class Box(ta.Generic[t_var]):  # type: ignore
        pass

    class IntBox(Box[int]):  # type: ignore
        pass

    typ = reflect_join(
        IntBox,
        Box[int],  # type: ignore
        RuntimeTypeReflector(RuntimeTypeUniverse(dynamic_type_name_suffix=DYNAMIC_TYPE_NAME_COUNTER)),
    )

    assert isinstance(typ, types.Instance)
    assert typ.type.fullname.endswith('.Box@2')
    assert [type_str(arg) for arg in typ.args] == ['builtins.int']


def test_runtime_constraints_solve_generic_base_type_var() -> None:
    t_var = ta.TypeVar('T')  # type: ignore

    class Box(ta.Generic[t_var]):  # type: ignore
        pass

    class IntBox(Box[int]):  # type: ignore
        pass

    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    template = reflector.reflect_type(Box[t_var])  # type: ignore
    actual = reflector.reflect_type(IntBox)

    assert isinstance(template, types.Instance)
    assert isinstance(actual, types.Instance)
    assert len(template.type.type_vars) == 1

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)
    solution = solve_constraints([template.type.type_vars[0]], constraints)

    assert [constraint.op for constraint in constraints] == [ConstraintOp.SUPERTYPE_OF, ConstraintOp.SUBTYPE_OF]
    assert [type_str(ta.cast(types.Type, item)) for item in solution] == ['builtins.int']


def test_runtime_constraints_use_reflected_covariant_type_var() -> None:
    t_co = ta.TypeVar('T_co', covariant=True)  # type: ignore

    class Box(ta.Generic[t_co]):  # type: ignore
        pass

    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    template = reflector.reflect_type(Box[t_co])  # type: ignore
    actual = reflector.reflect_type(Box[int])  # type: ignore

    assert isinstance(template, types.Instance)
    assert template.type.variances == [symbols.VarianceKind.CO]

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)
    solution = solve_constraints([template.type.type_vars[0]], constraints)

    assert [constraint.op for constraint in constraints] == [ConstraintOp.SUPERTYPE_OF]
    assert [type_str(ta.cast(types.Type, item)) for item in solution] == ['builtins.int']


def test_runtime_constraints_use_reflected_contravariant_type_var() -> None:
    t_contra = ta.TypeVar('T_contra', contravariant=True)  # type: ignore

    class Sink(ta.Generic[t_contra]):  # type: ignore
        pass

    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    template = reflector.reflect_type(Sink[t_contra])  # type: ignore
    actual = reflector.reflect_type(Sink[int])  # type: ignore

    assert isinstance(template, types.Instance)
    assert template.type.variances == [symbols.VarianceKind.CONTRA]

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)
    solution = solve_constraints([template.type.type_vars[0]], constraints)

    assert [constraint.op for constraint in constraints] == [ConstraintOp.SUBTYPE_OF]
    assert [type_str(ta.cast(types.Type, item)) for item in solution] == ['builtins.int']


def test_runtime_constraints_solve_type_type_wrapped_generic() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    template = types.TypeType(reflector.reflect_type(list[t_var]))  # type: ignore
    actual = types.TypeType(reflector.reflect_type(list[int]))

    assert isinstance(template.item, types.Instance)
    assert isinstance(template.item.args[0], types.TypeVarLikeType)

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)
    solution = solve_constraints([template.item.args[0]], constraints)

    assert [type_str(ta.cast(types.Type, item)) for item in solution] == ['builtins.int']


def test_runtime_constraints_solve_reflected_generic_alias_template() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    alias = ta.TypeAliasType('Alias', list[t_var], type_params=(t_var,))  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    template = reflector.reflect_type(alias[t_var])
    actual = reflector.reflect_type(list[int])

    assert isinstance(template, types.TypeAliasType)
    assert isinstance(template.args[0], types.TypeVarLikeType)

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)
    solution = solve_constraints([template.args[0]], constraints)

    assert [constraint.op for constraint in constraints] == [ConstraintOp.SUPERTYPE_OF, ConstraintOp.SUBTYPE_OF]
    assert [type_str(ta.cast(types.Type, item)) for item in solution] == ['builtins.int']


def test_runtime_constraints_solve_reflected_optional_type_var() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    template = reflector.reflect_type(ta.Optional[t_var])  # noqa
    actual = reflector.reflect_type(ta.Optional[int])  # noqa

    assert isinstance(template, types.UnionType)
    reflected_t_var = next(item for item in template.items if isinstance(item, types.TypeVarLikeType))

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)
    solution = solve_constraints([reflected_t_var], constraints)

    assert [constraint.op for constraint in constraints] == [ConstraintOp.SUPERTYPE_OF]
    assert [type_str(ta.cast(types.Type, item)) for item in solution] == ['builtins.int']


def test_runtime_constraints_solve_reflected_optional_collection_alias_template() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    alias = ta.TypeAliasType('MaybeList', list[t_var] | None, type_params=(t_var,))  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    template = reflector.reflect_type(alias[t_var])
    actual = reflector.reflect_type(list[int] | None)

    assert isinstance(template, types.TypeAliasType)
    assert isinstance(template.args[0], types.TypeVarLikeType)

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)
    solution = solve_constraints([template.args[0]], constraints)

    assert [constraint.op for constraint in constraints] == [ConstraintOp.SUPERTYPE_OF, ConstraintOp.SUBTYPE_OF]
    assert [type_str(ta.cast(types.Type, item)) for item in solution] == ['builtins.int']


def test_runtime_constraints_solve_reflected_fixed_tuple_template() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    template = reflector.reflect_type(tuple[t_var, str])  # type: ignore
    actual = reflector.reflect_type(tuple[int, str])

    assert isinstance(template, types.TupleType)
    assert isinstance(template.items[0], types.TypeVarLikeType)

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)
    solution = solve_constraints([template.items[0]], constraints)

    assert [constraint.op for constraint in constraints] == [ConstraintOp.SUPERTYPE_OF]
    assert [type_str(ta.cast(types.Type, item)) for item in solution] == ['builtins.int']


def test_runtime_constraints_solve_reflected_fixed_tuple_with_subtype_compatible_concrete_item() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    template = reflector.reflect_type(tuple[t_var, object])  # type: ignore
    actual = reflector.reflect_type(tuple[int, str])

    assert isinstance(template, types.TupleType)
    assert isinstance(template.items[0], types.TypeVarLikeType)

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)
    solution = solve_constraints([template.items[0]], constraints)

    assert [constraint.op for constraint in constraints] == [ConstraintOp.SUPERTYPE_OF]
    assert [type_str(ta.cast(types.Type, item)) for item in solution] == ['builtins.int']


def test_runtime_constraints_solve_reflected_join_derived_fixed_tuple_shape() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    joined = reflect_join(tuple[int, object], tuple[object, str], reflector)
    template = reflector.reflect_type(tuple[t_var, object])  # type: ignore

    assert isinstance(joined, types.TupleType)
    assert [type_str(item) for item in joined.items] == ['builtins.object', 'builtins.object']
    assert isinstance(template, types.TupleType)
    assert isinstance(template.items[0], types.TypeVarLikeType)

    constraints = infer_constraints(template, joined, ConstraintOp.SUPERTYPE_OF)
    solution = solve_constraints([template.items[0]], constraints)

    assert [constraint.op for constraint in constraints] == [ConstraintOp.SUPERTYPE_OF]
    assert [type_str(ta.cast(types.Type, item)) for item in solution] == ['builtins.object']


def test_runtime_constraints_solve_reflected_meet_derived_fixed_tuple_shape() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    met = reflect_meet(tuple[int, object], tuple[object, str], reflector)
    template = reflector.reflect_type(tuple[t_var, str])  # type: ignore

    assert isinstance(met, types.TupleType)
    assert [type_str(item) for item in met.items] == ['builtins.int', 'builtins.str']
    assert isinstance(template, types.TupleType)
    assert isinstance(template.items[0], types.TypeVarLikeType)

    constraints = infer_constraints(template, met, ConstraintOp.SUPERTYPE_OF)
    solution = solve_constraints([template.items[0]], constraints)

    assert [constraint.op for constraint in constraints] == [ConstraintOp.SUPERTYPE_OF]
    assert [type_str(ta.cast(types.Type, item)) for item in solution] == ['builtins.int']


def test_runtime_constraints_solve_reflected_tuple_type_var_tuple_template() -> None:
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    template = reflector.reflect_type(tuple[ta.Unpack[ts_var]])  # type: ignore  # noqa
    actual = reflector.reflect_type(tuple[int, str])

    assert isinstance(template, types.TupleType)
    assert isinstance(template.items[0], types.UnpackType)
    assert isinstance(template.items[0].type, types.TypeVarTupleType)

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)
    solution = solve_constraints([template.items[0].type], constraints)

    assert isinstance(solution[0], types.TupleType)
    assert [type_str(item) for item in solution[0].items] == ['builtins.int', 'builtins.str']


def test_runtime_constraints_solve_reflected_tuple_type_var_tuple_between_prefix_and_suffix() -> None:
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    template = reflector.reflect_type(tuple[int, ta.Unpack[ts_var], bytes])  # type: ignore  # noqa
    actual = reflector.reflect_type(tuple[int, str, bool, bytes])

    assert isinstance(template, types.TupleType)
    assert isinstance(template.items[1], types.UnpackType)
    assert isinstance(template.items[1].type, types.TypeVarTupleType)

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)
    solution = solve_constraints([template.items[1].type], constraints)

    assert isinstance(solution[0], types.TupleType)
    assert [type_str(item) for item in solution[0].items] == ['builtins.str', 'builtins.bool']


def test_runtime_constraints_solve_reflected_tuple_type_var_tuple_alias_template() -> None:
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    alias = ta.TypeAliasType('Packed', tuple[*ts_var], type_params=(ts_var,))  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    template = reflector.reflect_type(alias)
    actual = reflector.reflect_type(tuple[int, str])

    assert isinstance(template, types.TypeAliasType)
    assert template.alias is not None
    assert len(template.alias.alias_tvars) == 1
    assert isinstance(template.alias.alias_tvars[0], types.TypeVarTupleType)

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)
    solution = solve_constraints([template.alias.alias_tvars[0]], constraints)

    assert isinstance(solution[0], types.TupleType)
    assert [type_str(item) for item in solution[0].items] == ['builtins.int', 'builtins.str']


def test_runtime_constraints_accept_reflected_subscripted_tuple_type_var_tuple_alias() -> None:
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    alias = ta.TypeAliasType('Packed', tuple[*ts_var], type_params=(ts_var,))  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    template = reflector.reflect_type(alias[int, str])
    actual = reflector.reflect_type(tuple[int, str])

    assert isinstance(template, types.TypeAliasType)
    assert len(template.args) == 1
    assert isinstance(template.args[0], types.TupleType)

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)

    assert constraints == []


def test_runtime_constraints_accept_reflected_subscripted_mixed_type_var_tuple_alias() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    u_var = ta.TypeVar('U')  # type: ignore
    alias = ta.TypeAliasType('Mixed', tuple[t_var, *ts_var, u_var], type_params=(t_var, ts_var, u_var))  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    template = reflector.reflect_type(alias[int, str, bool, bytes])
    actual = reflector.reflect_type(tuple[int, str, bool, bytes])

    assert isinstance(template, types.TypeAliasType)
    assert [type_str(arg) for arg in template.args] == [
        'builtins.int',
        'tuple[builtins.str, builtins.bool]',
        'builtins.bytes',
    ]

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)

    assert constraints == []


def test_runtime_constraints_solve_reflected_variadic_alias_with_packed_template_arg() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    alias = ta.TypeAliasType('PackedTail', tuple[t_var, *ts_var], type_params=(t_var, ts_var))  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    template = reflector.reflect_type(alias[t_var, str, bool])
    actual = reflector.reflect_type(tuple[int, str, bool])

    assert isinstance(template, types.TypeAliasType)
    assert len(template.args) == 2
    assert isinstance(template.args[0], types.TypeVarLikeType)
    assert isinstance(template.args[1], types.TupleType)
    assert [type_str(item) for item in template.args[1].items] == ['builtins.str', 'builtins.bool']

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)
    solution = solve_constraints([template.args[0]], constraints)

    assert [constraint.op for constraint in constraints] == [ConstraintOp.SUPERTYPE_OF]
    assert [type_str(ta.cast(types.Type, item)) for item in solution] == ['builtins.int']


def test_runtime_constraints_solve_reflected_variadic_alias_with_packed_actual_arg() -> None:
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    alias = ta.TypeAliasType('Packed', tuple[*ts_var], type_params=(ts_var,))  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    template = reflector.reflect_type(tuple[*ts_var])  # type: ignore
    actual = reflector.reflect_type(alias[int, str])

    assert isinstance(template, types.TupleType)
    assert isinstance(template.items[0], types.UnpackType)
    assert isinstance(template.items[0].type, types.TypeVarTupleType)
    assert isinstance(actual, types.TypeAliasType)
    assert len(actual.args) == 1
    assert isinstance(actual.args[0], types.TupleType)
    assert [type_str(item) for item in actual.args[0].items] == ['builtins.int', 'builtins.str']

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)
    solution = solve_constraints([template.items[0].type], constraints)

    assert isinstance(solution[0], types.TupleType)
    assert [type_str(item) for item in solution[0].items] == ['builtins.int', 'builtins.str']


def test_runtime_constraints_solve_reflected_optional_tuple_alias_template() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    alias = ta.TypeAliasType('MaybePair', tuple[t_var, str] | None, type_params=(t_var,))  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    template = reflector.reflect_type(alias[t_var])
    actual = reflector.reflect_type(tuple[int, str] | None)

    assert isinstance(template, types.TypeAliasType)
    assert isinstance(template.args[0], types.TypeVarLikeType)

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)
    solution = solve_constraints([template.args[0]], constraints)

    assert [constraint.op for constraint in constraints] == [ConstraintOp.SUPERTYPE_OF]
    assert [type_str(ta.cast(types.Type, item)) for item in solution] == ['builtins.int']


def test_runtime_constraints_fail_closed_for_ambiguous_reflected_union_template() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    u_var = ta.TypeVar('U')  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    with pytest.raises(UnsupportedTypeOperationError, match='ambiguous Union'):
        infer_constraints(
            reflector.reflect_type(t_var | u_var),
            reflector.reflect_type(int | str),
            ConstraintOp.SUPERTYPE_OF,
        )


def test_runtime_constraints_unroll_reflected_recursive_alias_template() -> None:
    alias = ta.TypeAliasType('Node', int | list['Node'])  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    constraints = infer_constraints(
        reflector.reflect_type(alias),
        reflector.reflect_type(int | list[alias]),  # type: ignore
        ConstraintOp.SUPERTYPE_OF,
    )

    assert constraints == []


def test_runtime_constraints_unroll_reflected_json_like_recursive_alias_template_and_actual() -> None:
    alias = ta.TypeAliasType(  # type: ignore
        'Jsonish',
        type(None) | bool | int | str | list['Jsonish'] | dict[str, 'Jsonish'],  # type: ignore[name-defined]
    )
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse(), forward_ref_resolver={'Jsonish': alias}.__getitem__)
    unrolled = type(None) | bool | int | str | list[alias] | dict[str, alias]  # type: ignore

    assert infer_constraints(
        reflector.reflect_type(alias),
        reflector.reflect_type(unrolled),
        ConstraintOp.SUPERTYPE_OF,
    ) == []
    assert infer_constraints(
        reflector.reflect_type(unrolled),
        reflector.reflect_type(alias),
        ConstraintOp.SUPERTYPE_OF,
    ) == []


def test_runtime_constraints_unroll_reflected_recursive_alias_with_literal_and_newtype_leaves() -> None:
    user_id = ta.NewType('UserId', int)  # type: ignore
    alias = ta.TypeAliasType(  # type: ignore
        'TaggedNode',
        ta.Literal['user'] | user_id | list['TaggedNode'],  # type: ignore[name-defined]
    )
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse(), forward_ref_resolver={'TaggedNode': alias}.__getitem__)
    unrolled = ta.Literal['user'] | user_id | list[alias]  # type: ignore

    assert infer_constraints(
        reflector.reflect_type(alias),
        reflector.reflect_type(unrolled),
        ConstraintOp.SUPERTYPE_OF,
    ) == []
    assert infer_constraints(
        reflector.reflect_type(unrolled),
        reflector.reflect_type(alias),
        ConstraintOp.SUPERTYPE_OF,
    ) == []


def test_runtime_constraints_solve_reflected_repeated_recursive_alias_type_var_positions() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    alias = ta.TypeAliasType(  # type: ignore
        'PairNode',
        tuple[t_var, t_var, 'PairNode[T]'],  # type: ignore[name-defined, valid-type]
        type_params=(t_var,),
    )
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse(), forward_ref_resolver={'PairNode': alias}.__getitem__)
    template = reflector.reflect_type(alias[t_var])
    actual = reflector.reflect_type(tuple[int, int, alias[int]])  # type: ignore

    assert isinstance(template, types.TypeAliasType)
    assert template.alias is not None
    assert isinstance(template.alias.alias_tvars[0], types.TypeVarType)

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)
    solution = solve_constraints([template.alias.alias_tvars[0]], constraints)

    assert constraints
    assert [type_str(ta.cast(types.Type, item)) for item in solution] == ['builtins.int']
    assert solution[0] is not None
    substituted = substitute_type(template, {template.alias.alias_tvars[0]: solution[0]})
    assert reflector.structural_type_key(substituted) == reflector.structural_type_key(actual)


def test_runtime_constraints_solve_reflected_repeated_recursive_alias_bounds_structurally() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    alias = ta.TypeAliasType('Node', int | list['Node'])  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse(), forward_ref_resolver={'Node': alias}.__getitem__)
    template = reflector.reflect_type(tuple[t_var, t_var])  # type: ignore
    actual = reflector.reflect_type(tuple[alias, int | list[alias]])  # type: ignore
    reflected_t_var = reflector.reflect_type(t_var)

    assert isinstance(reflected_t_var, types.TypeVarType)

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)
    solution = solve_constraints([reflected_t_var], constraints)

    assert solution[0] is not None
    assert reflector.structural_type_key(solution[0]) == reflect_structural_type_key(alias, reflector)


def test_runtime_constraints_solve_reflected_variadic_recursive_alias_template() -> None:
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    alias = ta.TypeAliasType('TupleNode', tuple[*ts_var, 'TupleNode[*Ts]'], type_params=(ts_var,))  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse(), forward_ref_resolver={'TupleNode': alias}.__getitem__)
    template = reflector.reflect_type(alias[ts_var])
    actual = reflector.reflect_type(tuple[int, str, alias[int, str]])  # type: ignore

    assert isinstance(template, types.TypeAliasType)
    assert template.alias is not None
    assert isinstance(template.alias.alias_tvars[0], types.TypeVarTupleType)

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)
    solution = solve_constraints([template.alias.alias_tvars[0]], constraints)

    assert isinstance(solution[0], types.TupleType)
    assert [type_str(item) for item in solution[0].items] == ['builtins.int', 'builtins.str']


def test_runtime_constraints_solve_reflected_mixed_recursive_alias_template() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    alias = ta.TypeAliasType(  # type: ignore
        'MixedNode',
        tuple[t_var, *ts_var, 'MixedNode[T, *Ts]'],  # type: ignore[name-defined, valid-type]
        type_params=(t_var, ts_var),
    )
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse(), forward_ref_resolver={'MixedNode': alias}.__getitem__)
    template = reflector.reflect_type(alias[t_var, *ts_var])
    actual = reflector.reflect_type(tuple[str, int, bool, alias[str, int, bool]])  # type: ignore

    assert isinstance(template, types.TypeAliasType)
    assert template.alias is not None
    assert isinstance(template.alias.alias_tvars[0], types.TypeVarType)
    assert isinstance(template.alias.alias_tvars[1], types.TypeVarTupleType)

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)
    solution = solve_constraints(list(template.alias.alias_tvars), constraints)

    assert [type_str(ta.cast(types.Type, item)) for item in solution] == [
        'builtins.str',
        'tuple[builtins.int, builtins.bool]',
    ]
    assert solution[0] is not None
    assert solution[1] is not None
    substituted = substitute_type(
        template,
        {
            template.alias.alias_tvars[0]: solution[0],
            template.alias.alias_tvars[1]: solution[1],
        },
    )
    assert reflector.structural_type_key(substituted) == reflector.structural_type_key(actual)


def test_runtime_constraints_solve_reflected_callable_template() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    template = reflector.reflect_type(cabc.Callable[[t_var], t_var])
    actual = reflector.reflect_type(cabc.Callable[[int], int])

    assert isinstance(template, types.CallableType)
    assert isinstance(template.arg_types[0], types.TypeVarLikeType)

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)
    solution = solve_constraints([template.arg_types[0]], constraints)

    assert [constraint.op for constraint in constraints] == [ConstraintOp.SUPERTYPE_OF, ConstraintOp.SUBTYPE_OF]
    assert [type_str(ta.cast(types.Type, item)) for item in solution] == ['builtins.int']


def test_runtime_constraints_solve_reflected_callable_param_spec_template() -> None:
    param_spec = ta.ParamSpec('P')  # type: ignore
    ret_var = ta.TypeVar('R')  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    template = reflector.reflect_type(cabc.Callable[param_spec, ret_var])
    actual = reflector.reflect_type(cabc.Callable[[int, str], bool])

    assert isinstance(template, types.CallableType)
    assert isinstance(template.variables[0], types.ParamSpecType)
    assert isinstance(template.ret_type, types.TypeVarLikeType)

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)
    solution = solve_constraints([template.ret_type, template.variables[0]], constraints)

    assert [constraint.op for constraint in constraints] == [ConstraintOp.SUPERTYPE_OF, ConstraintOp.SUBTYPE_OF]
    assert type_str(ta.cast(types.Type, solution[0])) == 'builtins.bool'
    assert isinstance(solution[1], types.Parameters)
    assert [type_str(arg) for arg in solution[1].arg_types] == ['builtins.int', 'builtins.str']
    assert solution[1].arg_kinds == [symbols.ArgKind.POS, symbols.ArgKind.POS]
    assert solution[1].arg_names == [None, None]


def test_runtime_constraints_solve_repeated_reflected_callable_param_spec_template() -> None:
    param_spec = ta.ParamSpec('P')  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    left_template = reflector.reflect_type(cabc.Callable[param_spec, int])
    right_template = reflector.reflect_type(cabc.Callable[param_spec, str])
    left_actual = reflector.reflect_type(cabc.Callable[[int], int])
    right_actual = reflector.reflect_type(cabc.Callable[[int], str])

    assert isinstance(left_template, types.CallableType)
    assert isinstance(right_template, types.CallableType)
    assert isinstance(left_template.variables[0], types.ParamSpecType)

    constraints = [
        *infer_constraints(left_template, left_actual, ConstraintOp.SUPERTYPE_OF),
        *infer_constraints(right_template, right_actual, ConstraintOp.SUPERTYPE_OF),
    ]
    solution = solve_constraints([left_template.variables[0]], constraints)

    assert isinstance(solution[0], types.Parameters)
    assert [type_str(arg) for arg in solution[0].arg_types] == ['builtins.int']


def test_runtime_constraints_solve_reflected_callable_concatenate_template() -> None:
    param_spec = ta.ParamSpec('P')  # type: ignore
    ret_var = ta.TypeVar('R')  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    template = reflector.reflect_type(cabc.Callable[ta.Concatenate[int, param_spec], ret_var])
    actual = reflector.reflect_type(cabc.Callable[[int, str], bool])

    assert isinstance(template, types.CallableType)
    assert isinstance(template.variables[0], types.ParamSpecType)
    assert isinstance(template.ret_type, types.TypeVarLikeType)

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)
    solution = solve_constraints([template.ret_type, template.variables[0]], constraints)

    assert [constraint.op for constraint in constraints] == [ConstraintOp.SUPERTYPE_OF, ConstraintOp.SUBTYPE_OF]
    assert type_str(ta.cast(types.Type, solution[0])) == 'builtins.bool'
    assert isinstance(solution[1], types.Parameters)
    assert [type_str(arg) for arg in solution[1].arg_types] == ['builtins.str']


def test_runtime_constraints_solve_reflected_overloaded_callable_param_spec_template() -> None:
    param_spec = ta.ParamSpec('P')  # type: ignore
    ret_var = ta.TypeVar('R')  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    template = types.Overloaded([
        ta.cast(types.CallableType, reflector.reflect_type(cabc.Callable[[str], ret_var])),
        ta.cast(types.CallableType, reflector.reflect_type(cabc.Callable[param_spec, ret_var])),
    ])
    actual = reflector.reflect_type(cabc.Callable[[int, str], bool])

    assert isinstance(actual, types.CallableType)
    assert isinstance(template.items[1].variables[0], types.ParamSpecType)
    assert isinstance(template.items[1].ret_type, types.TypeVarLikeType)

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)
    solution = solve_constraints([template.items[1].ret_type, template.items[1].variables[0]], constraints)

    assert [constraint.op for constraint in constraints] == [ConstraintOp.SUPERTYPE_OF, ConstraintOp.SUBTYPE_OF]
    assert type_str(ta.cast(types.Type, solution[0])) == 'builtins.bool'
    assert isinstance(solution[1], types.Parameters)
    assert [type_str(arg) for arg in solution[1].arg_types] == ['builtins.int', 'builtins.str']


def test_runtime_constraints_solve_reflected_overloaded_callable_concatenate_template() -> None:
    param_spec = ta.ParamSpec('P')  # type: ignore
    ret_var = ta.TypeVar('R')  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    template = types.Overloaded([
        ta.cast(types.CallableType, reflector.reflect_type(cabc.Callable[ta.Concatenate[str, param_spec], ret_var])),
        ta.cast(types.CallableType, reflector.reflect_type(cabc.Callable[ta.Concatenate[int, param_spec], ret_var])),
    ])
    actual = reflector.reflect_type(cabc.Callable[[int, str], bool])

    assert isinstance(actual, types.CallableType)
    assert isinstance(template.items[1].variables[0], types.ParamSpecType)
    assert isinstance(template.items[1].ret_type, types.TypeVarLikeType)

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)
    solution = solve_constraints([template.items[1].ret_type, template.items[1].variables[0]], constraints)

    assert [constraint.op for constraint in constraints] == [ConstraintOp.SUPERTYPE_OF, ConstraintOp.SUBTYPE_OF]
    assert type_str(ta.cast(types.Type, solution[0])) == 'builtins.bool'
    assert isinstance(solution[1], types.Parameters)
    assert [type_str(arg) for arg in solution[1].arg_types] == ['builtins.str']


def test_runtime_constraints_fail_closed_for_ambiguous_reflected_overloaded_param_spec_items() -> None:
    left_param_spec = ta.ParamSpec('P')  # type: ignore
    right_param_spec = ta.ParamSpec('Q')  # type: ignore
    ret_var = ta.TypeVar('R')  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    template = types.Overloaded([
        ta.cast(types.CallableType, reflector.reflect_type(cabc.Callable[left_param_spec, ret_var])),
        ta.cast(types.CallableType, reflector.reflect_type(cabc.Callable[right_param_spec, ret_var])),
    ])
    actual = reflector.reflect_type(cabc.Callable[[int], bool])

    with pytest.raises(UnsupportedTypeOperationError, match='2 matches'):
        infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)


def test_runtime_constraints_fail_closed_for_reflected_callable_concatenate_prefix_mismatch() -> None:
    param_spec = ta.ParamSpec('P')  # type: ignore
    ret_var = ta.TypeVar('R')  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    template = reflector.reflect_type(cabc.Callable[ta.Concatenate[int, param_spec], ret_var])
    actual = reflector.reflect_type(cabc.Callable[[str], bool])

    with pytest.raises(UnsupportedTypeOperationError, match='instance constraint inference'):
        infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)


def test_runtime_constraints_fail_closed_for_reflected_callable_ellipsis_template() -> None:
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    template = reflector.reflect_type(cabc.Callable[..., int])
    actual = reflector.reflect_type(cabc.Callable[..., int])

    with pytest.raises(UnsupportedTypeOperationError, match='ellipsis Callable'):
        infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)


def test_reflect_alpha_type_key_canonicalizes_runtime_type_vars() -> None:
    left_t = ta.TypeVar('T')  # type: ignore
    right_u = ta.TypeVar('U')  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    left_key = reflect_alpha_type_key(list[left_t], reflector)  # type: ignore
    right_key = reflect_alpha_type_key(list[right_u], reflector)  # type: ignore

    assert left_key == right_key
    assert reflect_alpha_type_key_or_none(list[left_t], reflector) == right_key  # type: ignore


def test_reflector_type_key_cache_reuses_key_objects() -> None:
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    typ = reflector.reflect_type(list[int])

    assert reflector.type_key(typ) is reflector.type_key(typ)
    assert reflector.type_key_or_none(typ) is reflector.type_key(typ)
    assert reflect_type_key(list[int], reflector) is reflector.type_key(typ)
    assert reflect_type_key_or_none(list[int], reflector) is reflector.type_key(typ)


def test_reflector_alpha_type_key_cache_reuses_key_objects() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    typ = reflector.reflect_type(list[t_var])  # type: ignore

    assert reflector.alpha_type_key(typ) is reflector.alpha_type_key(typ)
    assert reflector.alpha_type_key_or_none(typ) is reflector.alpha_type_key(typ)
    assert reflect_alpha_type_key(list[t_var], reflector) is reflector.alpha_type_key(typ)  # type: ignore
    assert reflect_alpha_type_key_or_none(list[t_var], reflector) is reflector.alpha_type_key(typ)  # type: ignore


def test_reflector_structural_type_key_cache_reuses_key_objects() -> None:
    alias = ta.TypeAliasType('Alias', list[int])  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    typ = reflector.reflect_type(alias)

    assert reflector.structural_type_key(typ) is reflector.structural_type_key(typ)
    assert reflector.structural_type_key_or_none(typ) is reflector.structural_type_key(typ)
    assert reflect_structural_type_key(alias, reflector) is reflector.structural_type_key(typ)
    assert reflect_structural_type_key_or_none(alias, reflector) is reflector.structural_type_key(typ)


def test_reflector_alpha_structural_type_key_cache_reuses_key_objects() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    alias = ta.TypeAliasType('Alias', list[t_var], type_params=(t_var,))  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    typ = reflector.reflect_type(alias[t_var])

    assert reflector.alpha_structural_type_key(typ) is reflector.alpha_structural_type_key(typ)
    assert reflector.alpha_structural_type_key_or_none(typ) is reflector.alpha_structural_type_key(typ)
    assert (
        reflect_alpha_structural_type_key(alias[t_var], reflector)
        is reflector.alpha_structural_type_key(typ)
    )
    assert (
        reflect_alpha_structural_type_key_or_none(alias[t_var], reflector)
        is reflector.alpha_structural_type_key(typ)
    )


def test_reflector_recursive_variadic_alias_structural_key_caches_are_hot_path_friendly() -> None:
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    alias = ta.TypeAliasType('TupleNode', tuple[*ts_var, 'TupleNode[*Ts]'], type_params=(ts_var,))  # type: ignore
    form = alias[int, str]
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse(), forward_ref_resolver={'TupleNode': alias}.__getitem__)
    typ = reflector.reflect_type(form)
    key = reflect_structural_type_key(form, reflector)
    alpha_key = reflect_alpha_structural_type_key(form, reflector)

    assert reflector.reflect_type(form) is typ
    assert reflect_structural_type_key(form, reflector) is key
    assert reflect_structural_type_key_or_none(form, reflector) is key
    assert reflector.structural_type_key(typ) is key
    assert reflector._structural_type_key_cache[typ] is key
    assert reflector._structural_type_key_or_none_cache[typ] is key
    assert reflect_alpha_structural_type_key(form, reflector) is alpha_key
    assert reflect_alpha_structural_type_key_or_none(form, reflector) is alpha_key
    assert reflector.alpha_structural_type_key(typ) is alpha_key
    assert reflector._alpha_structural_type_key_cache[typ] is alpha_key
    assert reflector._alpha_structural_type_key_or_none_cache[typ] is alpha_key


def test_reflector_type_key_or_none_cache_reuses_none_for_unsupported_type() -> None:
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    typ = types.PartialType(None, None)

    assert reflector.type_key_or_none(typ) is None
    assert reflector.type_key_or_none(typ) is None
    assert reflector._type_key_or_none_cache[typ] is None
    assert typ not in reflector._type_key_cache

    with pytest.raises(ReflectionError, match='not implemented'):
        reflector.type_key(typ)

    assert reflector._type_key_or_none_cache[typ] is None
    assert typ not in reflector._type_key_cache


def test_reflector_structural_type_key_or_none_cache_reuses_none_for_unsupported_recursive_alias() -> None:
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    alias_node = symbols.TypeAlias('Bad', types.AnyType(types.TypeOfAny.EXPLICIT))
    typ = types.TypeAliasType(alias_node, [])
    alias_node._target = types.UnionType([typ, types.PartialType(None, None)])

    assert reflector.structural_type_key_or_none(typ) is None
    assert reflector.structural_type_key_or_none(typ) is None
    assert reflector._structural_type_key_or_none_cache[typ] is None
    assert typ not in reflector._structural_type_key_cache

    with pytest.raises(ReflectionError, match='not implemented'):
        reflector.structural_type_key(typ)

    assert reflector.alpha_structural_type_key_or_none(typ) is None
    assert reflector.alpha_structural_type_key_or_none(typ) is None
    assert reflector._alpha_structural_type_key_or_none_cache[typ] is None
    assert typ not in reflector._alpha_structural_type_key_cache

    with pytest.raises(ReflectionError, match='not implemented'):
        reflector.alpha_structural_type_key(typ)


def test_reflector_structural_type_key_or_none_cache_reuses_none_for_bad_recursive_alias_args() -> None:
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    list_info = symbols.TypeInfo('builtins.list')
    int_type = types.Instance(symbols.TypeInfo('builtins.int'), [])
    str_type = types.Instance(symbols.TypeInfo('builtins.str'), [])
    t_var = types.TypeVarType(
        'T',
        'T',
        types.TypeVarId(1),
        [],
        types.AnyType(types.TypeOfAny.EXPLICIT),
        types.AnyType(types.TypeOfAny.EXPLICIT),
    )
    alias_node = symbols.TypeAlias(
        'BadGeneric',
        types.AnyType(types.TypeOfAny.EXPLICIT),
        alias_tvars=[t_var],
    )
    good_typ = types.TypeAliasType(alias_node, [t_var])
    bad_typ = types.TypeAliasType(alias_node, [int_type, str_type])
    alias_node._target = types.Instance(list_info, [good_typ])

    assert bad_typ.is_recursive
    assert reflector.structural_type_key_or_none(bad_typ) is None
    assert reflector.structural_type_key_or_none(bad_typ) is None
    assert reflector._structural_type_key_or_none_cache[bad_typ] is None
    assert bad_typ not in reflector._structural_type_key_cache

    with pytest.raises(ReflectionError, match='not implemented'):
        reflector.structural_type_key(bad_typ)

    assert reflector.alpha_structural_type_key_or_none(bad_typ) is None
    assert reflector.alpha_structural_type_key_or_none(bad_typ) is None
    assert reflector._alpha_structural_type_key_or_none_cache[bad_typ] is None
    assert bad_typ not in reflector._alpha_structural_type_key_cache

    with pytest.raises(ReflectionError, match='not implemented'):
        reflector.alpha_structural_type_key(bad_typ)


def test_reflect_alpha_type_key_canonicalizes_parameterized_recursive_alias_type() -> None:
    left_t = ta.TypeVar('T')  # type: ignore
    right_u = ta.TypeVar('U')  # type: ignore
    left_alias = ta.TypeAliasType('Left', list['Left[T]'], type_params=(left_t,))  # type: ignore
    right_alias = ta.TypeAliasType('Right', list['Right[U]'], type_params=(right_u,))  # type: ignore

    left_reflector = RuntimeTypeReflector(RuntimeTypeUniverse(), forward_ref_resolver={'Left': left_alias}.__getitem__)
    right_reflector = RuntimeTypeReflector(
        RuntimeTypeUniverse(),
        forward_ref_resolver={'Right': right_alias}.__getitem__,
    )

    assert reflect_type_key(left_alias[left_t], left_reflector) != reflect_type_key(
        right_alias[right_u],
        right_reflector,
    )
    assert reflect_alpha_type_key(left_alias[left_t], left_reflector) == reflect_alpha_type_key(
        right_alias[right_u],
        right_reflector,
    )


def test_reflect_is_alpha_equivalent_handles_parameterized_recursive_alias_type() -> None:
    left_t = ta.TypeVar('T')  # type: ignore
    right_u = ta.TypeVar('U')  # type: ignore
    left_alias = ta.TypeAliasType('Left', list['Left[T]'], type_params=(left_t,))  # type: ignore
    right_alias = ta.TypeAliasType('Right', list['Right[U]'], type_params=(right_u,))  # type: ignore
    aliases = {
        'Left': left_alias,
        'Right': right_alias,
    }
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse(), forward_ref_resolver=aliases.__getitem__)

    assert reflect_is_alpha_equivalent(left_alias[left_t], right_alias[right_u], reflector)
    assert not reflect_is_same_type(left_alias[left_t], right_alias[right_u], reflector)


def test_reflect_is_structurally_equivalent_expands_nonrecursive_alias() -> None:
    alias = ta.TypeAliasType('Alias', list[int])  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    assert not reflect_is_same_type(alias, list[int], reflector)
    assert reflect_is_structurally_equivalent(alias, list[int], reflector)
    assert reflect_type_key(alias, reflector) != reflect_type_key(list[int], reflector)
    assert reflect_structural_type_key(alias, reflector) == reflect_structural_type_key(list[int], reflector)


def test_reflect_is_structural_subtype_expands_nonrecursive_alias() -> None:
    alias = ta.TypeAliasType('Alias', list[int])  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    assert reflect_is_structural_subtype(alias, list[int], reflector)
    assert reflect_is_structural_subtype(list[int], alias, reflector)


def test_reflect_structural_comparison_handles_annotated_new_type_alias_mix() -> None:
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
    mode_list = ta.TypeAliasType('ModeList', list[mode])  # type: ignore
    other_mode = ta.NewType('OtherMode', ta.Literal['a', 'b'])  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    assert reflect_is_structurally_equivalent(
        ta.Annotated[mode_list, 'left'],  # noqa
        ta.Annotated[list[mode], 'right'],  # noqa
        reflector,
    )
    assert reflect_is_structural_subtype(ta.Annotated[mode_list, 'left'], list[mode], reflector)  # noqa
    assert not reflect_is_structurally_equivalent(mode_list, list[other_mode], reflector)  # noqa
    assert not reflect_is_structural_subtype_or_false(mode_list, list[other_mode], reflector)  # noqa
    annotated_key = reflect_structural_type_key(ta.Annotated[mode_list, 'left'], reflector)
    assert annotated_key == reflect_structural_type_key(list[mode], reflector)  # noqa
    assert reflect_structural_type_key(mode_list, reflector) != reflect_structural_type_key(
        list[other_mode],  # noqa
        reflector,
    )


def test_reflect_structural_or_false_helpers_suppress_unsupported_relations() -> None:
    t_var = ta.TypeVar('T')  # type: ignore

    class Box[T]:
        pass

    class Concrete:
        pass

    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    assert not reflect_is_structural_subtype_or_false(ta.Callable[[t_var], t_var], object, reflector)  # noqa
    assert not reflect_is_structurally_equivalent_or_false(Concrete, object, reflector)
    assert not reflect_is_alpha_structurally_equivalent_or_false(Concrete, object, reflector)
    assert reflect_is_structural_subtype_or_false(Box[int], Box[int], reflector)


def test_reflect_is_structurally_equivalent_handles_recursive_alias_unrolling() -> None:
    alias = ta.TypeAliasType('Node', int | list['Node'])  # type: ignore
    reflector = RuntimeTypeReflector(
        RuntimeTypeUniverse(),
        forward_ref_resolver={'Node': alias}.__getitem__,
    )

    assert reflect_is_structurally_equivalent(alias, int | list[alias], reflector)  # type: ignore
    assert reflect_structural_type_key(alias, reflector) == reflect_structural_type_key(
        int | list[alias],  # type: ignore
        reflector,
    )
    assert reflect_structural_type_key(alias, reflector) == reflect_structural_type_key(
        int | list[int | list[alias]],  # type: ignore
        reflector,
    )


def test_reflect_structural_type_key_matches_equivalent_concrete_recursive_aliases() -> None:
    left_t = ta.TypeVar('T')  # type: ignore
    right_u = ta.TypeVar('U')  # type: ignore
    left_alias = ta.TypeAliasType('Left', left_t | list['Left[T]'], type_params=(left_t,))  # type: ignore
    right_alias = ta.TypeAliasType('Right', right_u | list['Right[U]'], type_params=(right_u,))  # type: ignore
    aliases = {
        'Left': left_alias,
        'Right': right_alias,
    }
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse(), forward_ref_resolver=aliases.__getitem__)

    left_int = left_alias[int]
    right_int = right_alias[int]
    left_unrolled = int | list[left_int]  # type: ignore
    right_unrolled = list[right_int] | int  # type: ignore

    assert reflect_is_structurally_equivalent(left_int, right_int, reflector)
    assert reflect_is_structurally_equivalent(left_int, left_unrolled, reflector)
    assert reflect_is_structurally_equivalent(left_unrolled, right_unrolled, reflector)
    assert reflect_structural_type_key(left_int, reflector) == reflect_structural_type_key(right_int, reflector)
    assert reflect_structural_type_key(left_int, reflector) == reflect_structural_type_key(left_unrolled, reflector)
    assert reflect_structural_type_key(left_unrolled, reflector) == reflect_structural_type_key(
        right_unrolled,
        reflector,
    )


def test_reflect_structural_type_key_matches_mutual_recursive_one_unrolling() -> None:
    left_a = ta.TypeAliasType('LeftA', list['LeftB'])  # type: ignore
    left_b = ta.TypeAliasType('LeftB', list['LeftA'])  # type: ignore
    right_a = ta.TypeAliasType('RightA', list['RightB'])  # type: ignore
    right_b = ta.TypeAliasType('RightB', list['RightA'])  # type: ignore
    aliases = {
        'LeftA': left_a,
        'LeftB': left_b,
        'RightA': right_a,
        'RightB': right_b,
    }
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse(), forward_ref_resolver=aliases.__getitem__)

    assert reflect_is_structurally_equivalent(left_a, right_a, reflector)
    assert reflect_is_structurally_equivalent(left_a, list[left_b], reflector)  # type: ignore
    assert reflect_is_structurally_equivalent(list[left_b], list[right_b], reflector)  # type: ignore
    assert reflect_structural_type_key(left_a, reflector) == reflect_structural_type_key(right_a, reflector)
    assert reflect_structural_type_key(left_a, reflector) == reflect_structural_type_key(
        list[left_b],  # type: ignore
        reflector,
    )
    assert reflect_structural_type_key(list[left_b], reflector) == reflect_structural_type_key(  # type: ignore
        list[right_b],  # type: ignore
        reflector,
    )


def test_reflect_structural_type_key_differs_when_recursive_alias_equivalence_differs() -> None:
    left_alias = ta.TypeAliasType('Left', int | list['Left'])  # type: ignore
    right_alias = ta.TypeAliasType('Right', str | list['Right'])  # type: ignore
    reflector = RuntimeTypeReflector(
        RuntimeTypeUniverse(),
        forward_ref_resolver={'Left': left_alias, 'Right': right_alias}.__getitem__,
    )

    assert not reflect_is_structurally_equivalent(left_alias, right_alias, reflector)
    assert reflect_structural_type_key(left_alias, reflector) != reflect_structural_type_key(right_alias, reflector)


def test_reflect_structural_type_key_handles_recursive_callable_aliases() -> None:
    return_alias = ta.TypeAliasType('ReturnFn', ta.Callable[[int], 'ReturnFn'])  # type: ignore
    arg_alias = ta.TypeAliasType('ArgFn', ta.Callable[['ArgFn'], int])  # type: ignore
    aliases = {
        'ReturnFn': return_alias,
        'ArgFn': arg_alias,
    }
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse(), forward_ref_resolver=aliases.__getitem__)

    return_unrolled = ta.Callable[[int], return_alias]  # type: ignore
    arg_unrolled = ta.Callable[[arg_alias], int]  # type: ignore

    assert reflect_is_structurally_equivalent(return_alias, return_unrolled, reflector)
    assert reflect_is_structurally_equivalent(arg_alias, arg_unrolled, reflector)
    assert reflect_structural_type_key_or_none(return_alias, reflector) == reflect_structural_type_key(
        return_alias,
        reflector,
    )
    assert reflect_structural_type_key(return_alias, reflector) == reflect_structural_type_key(
        return_unrolled,
        reflector,
    )
    assert reflect_structural_type_key(arg_alias, reflector) == reflect_structural_type_key(arg_unrolled, reflector)


def test_reflect_structural_type_key_handles_recursive_callable_param_specs() -> None:
    param_spec = ta.ParamSpec('P')  # type: ignore
    alias = ta.TypeAliasType(  # type: ignore
        'Fn',
        ta.Callable[ta.Concatenate[int, param_spec], 'Fn[P]'],  # noqa
        type_params=(param_spec,),
    )
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse(), forward_ref_resolver={'Fn': alias}.__getitem__)
    unrolled = ta.Callable[ta.Concatenate[int, param_spec], alias[param_spec]]  # type: ignore

    assert reflect_is_structurally_equivalent(alias[param_spec], unrolled, reflector)
    assert reflect_structural_type_key(alias[param_spec], reflector) == reflect_structural_type_key(
        unrolled,
        reflector,
    )
    assert reflect_alpha_structural_type_key_or_none(alias[param_spec], reflector) == reflect_alpha_structural_type_key(
        alias[param_spec],
        reflector,
    )


def test_reflect_structural_type_key_handles_recursive_tuple_alias() -> None:
    alias = ta.TypeAliasType('NodeTuple', tuple[int, 'NodeTuple'])  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse(), forward_ref_resolver={'NodeTuple': alias}.__getitem__)
    unrolled = tuple[int, alias]  # type: ignore
    double_unrolled = tuple[int, tuple[int, alias]]  # type: ignore

    assert reflect_is_structurally_equivalent(alias, unrolled, reflector)
    assert reflect_is_structurally_equivalent(unrolled, double_unrolled, reflector)
    assert reflect_structural_type_key(alias, reflector) == reflect_structural_type_key(unrolled, reflector)
    assert reflect_structural_type_key(alias, reflector) == reflect_structural_type_key(double_unrolled, reflector)


def test_reflect_alpha_structural_type_key_handles_parameterized_recursive_tuple_alias() -> None:
    left_t = ta.TypeVar('T')  # type: ignore
    right_u = ta.TypeVar('U')  # type: ignore
    left_target = tuple[left_t, 'LeftTuple[T]']  # type: ignore
    right_target = tuple[right_u, 'RightTuple[U]']  # type: ignore
    left_alias = ta.TypeAliasType('LeftTuple', left_target, type_params=(left_t,))  # type: ignore
    right_alias = ta.TypeAliasType('RightTuple', right_target, type_params=(right_u,))  # type: ignore
    aliases = {
        'LeftTuple': left_alias,
        'RightTuple': right_alias,
    }
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse(), forward_ref_resolver=aliases.__getitem__)
    left_unrolled = tuple[left_t, left_alias[left_t]]  # type: ignore
    right_unrolled = tuple[right_u, right_alias[right_u]]  # type: ignore

    assert not reflect_is_structurally_equivalent(left_alias[left_t], right_alias[right_u], reflector)
    assert reflect_is_alpha_structurally_equivalent(left_alias[left_t], right_alias[right_u], reflector)
    assert reflect_alpha_structural_type_key(left_alias[left_t], reflector) == reflect_alpha_structural_type_key(
        right_alias[right_u],
        reflector,
    )
    assert reflect_alpha_structural_type_key(left_alias[left_t], reflector) == reflect_alpha_structural_type_key(
        right_unrolled,
        reflector,
    )
    assert reflect_alpha_structural_type_key(left_unrolled, reflector) == reflect_alpha_structural_type_key(
        right_unrolled,
        reflector,
    )


def test_reflect_structural_type_key_handles_recursive_mapping_alias() -> None:
    alias = ta.TypeAliasType('NodeMap', ta.Mapping[str, list['NodeMap']])  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse(), forward_ref_resolver={'NodeMap': alias}.__getitem__)
    unrolled = ta.Mapping[str, list[alias]]  # type: ignore
    double_unrolled = ta.Mapping[str, list[ta.Mapping[str, list[alias]]]]  # type: ignore

    assert reflect_is_structurally_equivalent(alias, unrolled, reflector)
    assert reflect_is_structurally_equivalent(unrolled, double_unrolled, reflector)
    assert reflect_structural_type_key(alias, reflector) == reflect_structural_type_key(unrolled, reflector)
    assert reflect_structural_type_key(alias, reflector) == reflect_structural_type_key(double_unrolled, reflector)


def test_reflect_structural_type_key_ignores_annotated_recursive_alias_metadata() -> None:
    target_alias = ta.TypeAliasType('TargetNode', ta.Annotated[int | list['TargetNode'], 'target'])  # type: ignore
    ref_alias = ta.TypeAliasType('RefNode', int | list[ta.Annotated['RefNode', 'ref']])  # type: ignore
    aliases = {
        'TargetNode': target_alias,
        'RefNode': ref_alias,
    }
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse(), forward_ref_resolver=aliases.__getitem__)

    target_unrolled = int | list[target_alias]  # type: ignore
    ref_unrolled = int | list[ref_alias]  # type: ignore

    assert reflect_is_structurally_equivalent(target_alias, target_unrolled, reflector)
    assert reflect_is_structurally_equivalent(ref_alias, ref_unrolled, reflector)
    assert reflect_structural_type_key(target_alias, reflector) == reflect_structural_type_key(
        target_unrolled,
        reflector,
    )
    assert reflect_structural_type_key(ref_alias, reflector) == reflect_structural_type_key(ref_unrolled, reflector)
    assert reflect_structural_type_key(target_alias, reflector) == reflect_structural_type_key(ref_alias, reflector)


def test_reflect_structural_type_key_preserves_newtype_identity_in_recursive_alias() -> None:
    user_id = ta.NewType('UserId', int)  # type: ignore
    account_id = ta.NewType('AccountId', int)  # type: ignore
    left_alias = ta.TypeAliasType('LeftNode', user_id | list['LeftNode'])  # type: ignore
    right_alias = ta.TypeAliasType('RightNode', account_id | list['RightNode'])  # type: ignore
    aliases = {
        'LeftNode': left_alias,
        'RightNode': right_alias,
    }
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse(), forward_ref_resolver=aliases.__getitem__)

    assert not reflect_is_structurally_equivalent(left_alias, right_alias, reflector)
    assert not reflect_is_alpha_structurally_equivalent(left_alias, right_alias, reflector)
    assert reflect_structural_type_key(left_alias, reflector) != reflect_structural_type_key(right_alias, reflector)
    assert reflect_alpha_structural_type_key(left_alias, reflector) != reflect_alpha_structural_type_key(
        right_alias,
        reflector,
    )


def test_reflect_structural_type_key_cache_reuses_recursive_alias_keys() -> None:
    alias = ta.TypeAliasType('NodeTuple', tuple[int, 'NodeTuple'])  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse(), forward_ref_resolver={'NodeTuple': alias}.__getitem__)
    typ = reflector.reflect_type(alias)
    key = reflect_structural_type_key(alias, reflector)
    alpha_key = reflect_alpha_structural_type_key(alias, reflector)

    assert reflect_structural_type_key(alias, reflector) is key
    assert reflect_structural_type_key_or_none(alias, reflector) is key
    assert reflector.structural_type_key(typ) is key
    assert reflector._structural_type_key_cache[typ] is key
    assert reflector._structural_type_key_or_none_cache[typ] is key
    assert reflect_alpha_structural_type_key(alias, reflector) is alpha_key
    assert reflect_alpha_structural_type_key_or_none(alias, reflector) is alpha_key
    assert reflector.alpha_structural_type_key(typ) is alpha_key
    assert reflector._alpha_structural_type_key_cache[typ] is alpha_key
    assert reflector._alpha_structural_type_key_or_none_cache[typ] is alpha_key


def test_reflect_structural_type_key_handles_variadic_recursive_tuple_alias() -> None:
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    alias = ta.TypeAliasType('TupleNode', tuple[*ts_var, 'TupleNode[*Ts]'], type_params=(ts_var,))  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse(), forward_ref_resolver={'TupleNode': alias}.__getitem__)
    typ = reflector.reflect_type(alias[int, str])
    unrolled = tuple[int, str, alias[int, str]]  # type: ignore

    assert isinstance(typ, types.TypeAliasType)
    assert typ.is_recursive
    assert reflect_structural_type_key(alias[int, str], reflector) == reflect_structural_type_key(unrolled, reflector)
    assert reflect_alpha_structural_type_key(alias[ts_var], reflector) == reflect_alpha_structural_type_key(
        alias[ta.TypeVarTuple('Us')],
        reflector,
    )


def test_reflect_is_structural_subtype_handles_recursive_alias_unrolling() -> None:
    alias = ta.TypeAliasType('Node', int | list['Node'])  # type: ignore
    reflector = RuntimeTypeReflector(
        RuntimeTypeUniverse(),
        forward_ref_resolver={'Node': alias}.__getitem__,
    )

    assert reflect_is_structural_subtype(alias, int | list[alias], reflector)  # type: ignore
    assert reflect_is_structural_subtype(int | list[alias], alias, reflector)  # type: ignore
    assert reflect_is_structural_subtype_or_false(alias, int | list[alias], reflector)  # type: ignore
    assert reflect_is_structurally_equivalent_or_false(alias, int | list[alias], reflector)  # type: ignore


def test_reflect_is_alpha_structurally_equivalent_handles_generic_recursive_aliases() -> None:
    left_t = ta.TypeVar('T')  # type: ignore
    right_u = ta.TypeVar('U')  # type: ignore
    left_alias = ta.TypeAliasType('Left', left_t | list['Left[T]'], type_params=(left_t,))  # type: ignore
    right_alias = ta.TypeAliasType('Right', right_u | list['Right[U]'], type_params=(right_u,))  # type: ignore
    aliases = {
        'Left': left_alias,
        'Right': right_alias,
    }
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse(), forward_ref_resolver=aliases.__getitem__)

    assert not reflect_is_structurally_equivalent(left_alias[left_t], right_alias[right_u], reflector)
    assert reflect_is_alpha_structurally_equivalent(left_alias[left_t], right_alias[right_u], reflector)
    assert reflect_alpha_structural_type_key(left_alias[left_t], reflector) == reflect_alpha_structural_type_key(
        right_alias[right_u],
        reflector,
    )
    left_key = reflect_alpha_structural_type_key(left_alias[left_t], reflector)
    right_key = reflect_alpha_structural_type_key(right_u | list[right_alias[right_u]], reflector)  # type: ignore
    assert left_key == right_key


def test_reflect_structural_type_key_json_like_recursive_alias_is_cache_grade() -> None:
    left_alias = ta.TypeAliasType(  # type: ignore
        'Jsonish',
        type(None) | bool | int | str | list['Jsonish'] | dict[str, 'Jsonish'],  # type: ignore[name-defined]
    )
    right_alias = ta.TypeAliasType(  # type: ignore
        'OtherJsonish',
        dict[str, 'OtherJsonish'] | list['OtherJsonish'] | str | int | bool | type(None),  # type: ignore[name-defined]
    )
    aliases = {
        'Jsonish': left_alias,
        'OtherJsonish': right_alias,
    }
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse(), forward_ref_resolver=aliases.__getitem__)
    left_unrolled = type(None) | bool | int | str | list[left_alias] | dict[str, left_alias]  # type: ignore
    right_unrolled = dict[str, right_alias] | list[right_alias] | str | int | bool | type(None)  # type: ignore
    left_type = reflector.reflect_type(left_alias)
    left_key = reflect_structural_type_key(left_alias, reflector)

    assert reflect_is_structurally_equivalent(left_alias, right_alias, reflector)
    assert reflect_is_structurally_equivalent(left_alias, left_unrolled, reflector)
    assert reflect_is_structurally_equivalent(left_unrolled, right_unrolled, reflector)
    assert reflect_structural_type_key(right_alias, reflector) == left_key
    assert reflect_structural_type_key(left_unrolled, reflector) == left_key
    assert reflect_structural_type_key(right_unrolled, reflector) == left_key
    assert reflector.reflect_type(left_alias) is left_type
    assert reflector.structural_type_key(left_type) is left_key
    assert reflector.structural_type_key_or_none(left_type) is left_key


def test_reflect_alpha_structural_type_key_recursive_alias_tracks_repeated_variable_positions() -> None:
    left_t = ta.TypeVar('T')  # type: ignore
    right_u = ta.TypeVar('U')  # type: ignore
    wrong_u = ta.TypeVar('WrongU')  # type: ignore
    wrong_v = ta.TypeVar('WrongV')  # type: ignore
    left_alias = ta.TypeAliasType(  # type: ignore
        'LeftPair',
        tuple[left_t, left_t, 'LeftPair[T]'],  # type: ignore[name-defined, valid-type]
        type_params=(left_t,),
    )
    right_alias = ta.TypeAliasType(  # type: ignore
        'RightPair',
        tuple[right_u, right_u, 'RightPair[U]'],  # type: ignore[name-defined, valid-type]
        type_params=(right_u,),
    )
    wrong_alias = ta.TypeAliasType(  # type: ignore
        'WrongPair',
        tuple[wrong_u, wrong_v, 'WrongPair[WrongU, WrongV]'],  # type: ignore[name-defined, valid-type]
        type_params=(wrong_u, wrong_v),
    )
    aliases = {
        'LeftPair': left_alias,
        'RightPair': right_alias,
        'WrongPair': wrong_alias,
    }
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse(), forward_ref_resolver=aliases.__getitem__)

    assert not reflect_is_structurally_equivalent(left_alias[left_t], right_alias[right_u], reflector)
    assert reflect_is_alpha_structurally_equivalent(left_alias[left_t], right_alias[right_u], reflector)
    assert not reflect_is_alpha_structurally_equivalent(left_alias[left_t], wrong_alias[wrong_u, wrong_v], reflector)
    assert reflect_alpha_structural_type_key(left_alias[left_t], reflector) == reflect_alpha_structural_type_key(
        right_alias[right_u],
        reflector,
    )
    assert reflect_alpha_structural_type_key(left_alias[left_t], reflector) != reflect_alpha_structural_type_key(
        wrong_alias[wrong_u, wrong_v],
        reflector,
    )


def test_reflect_structural_type_key_recursive_alias_with_float_literals_is_order_insensitive() -> None:
    left_alias = ta.TypeAliasType(  # type: ignore
        'LeftFloatNode',
        ta.Literal[1.5, 2.5] | list['LeftFloatNode'],  # type: ignore[name-defined]
    )
    right_alias = ta.TypeAliasType(  # type: ignore
        'RightFloatNode',
        list['RightFloatNode'] | ta.Literal[2.5, 1.5],  # type: ignore[name-defined]
    )
    aliases = {
        'LeftFloatNode': left_alias,
        'RightFloatNode': right_alias,
    }
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse(), forward_ref_resolver=aliases.__getitem__)
    unrolled = list[left_alias] | ta.Literal[2.5, 1.5]  # type: ignore

    assert reflect_is_structurally_equivalent(left_alias, right_alias, reflector)
    assert reflect_is_structurally_equivalent(left_alias, unrolled, reflector)
    assert reflect_structural_type_key(left_alias, reflector) == reflect_structural_type_key(right_alias, reflector)
    assert reflect_structural_type_key(left_alias, reflector) == reflect_structural_type_key(unrolled, reflector)


def test_reflect_type_key_hot_path_reuses_reflection_and_key_caches() -> None:
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    forms = [
        int,
        list[int],
        ta.Mapping[str, ta.Sequence[int]],
        ta.Literal['red', 'blue'],
        ta.Literal[b'red', b'blue'],
        ta.Literal[None],
        ta.Literal[1.5, 2.5],
    ]

    for form in forms:
        typ = reflector.reflect_type(form)
        key = reflect_type_key(form, reflector)

        assert reflector.reflect_type(form) is typ
        assert reflect_type_key(form, reflector) is key
        assert reflect_type_key_or_none(form, reflector) is key
        assert reflector.type_key(typ) is key


def test_reflect_type_key_normalizes_none_type_but_keeps_none_literal_distinct() -> None:
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    none_key = reflect_type_key(None, reflector)
    none_type_key = reflect_type_key(type(None), reflector)
    none_literal_key = reflect_type_key(ta.Literal[None], reflector)

    assert none_key == 'None'
    assert none_type_key == 'None'  # type: ignore
    assert none_literal_key == "L[None:,I['builtins.None']]"
    assert none_literal_key != none_key


def test_reflect_type_key_normalizes_optional_forms() -> None:
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    key = reflect_type_key(int | None, reflector)

    assert reflect_type_key(ta.Optional[int], reflector) == key  # noqa
    assert reflect_type_key(ta.Union[int, None], reflector) == key  # noqa
    assert reflect_type_key(None | int, reflector) == key


def test_reflect_type_key_normalizes_literal_union_forms() -> None:
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    key = reflect_type_key(ta.Literal['x', 'y', None], reflector)

    assert reflect_type_key(ta.Literal['x'] | ta.Literal['y'] | ta.Literal[None], reflector) == key  # noqa
    assert reflect_type_key(ta.Literal[None, 'y', 'x'], reflector) == key


def test_reflect_type_key_literal_unions_are_order_insensitive_for_scalar_and_opaque_values() -> None:
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    left = ta.Literal[b'a', None, 1.5] | ta.Literal[2.5]  # type: ignore  # noqa
    right = ta.Literal[2.5] | ta.Literal[1.5, None, b'a']  # type: ignore  # noqa

    assert reflect_type_key(left, reflector) == reflect_type_key(right, reflector)


def test_reflect_join_with_different_runtime_generic_base_arg_returns_union() -> None:
    t_var = ta.TypeVar('T')  # type: ignore

    class Box(ta.Generic[t_var]):  # type: ignore
        pass

    class IntBox(Box[int]):  # type: ignore
        pass

    typ = reflect_join(
        IntBox,
        Box[str],  # type: ignore
        RuntimeTypeReflector(RuntimeTypeUniverse(dynamic_type_name_suffix=DYNAMIC_TYPE_NAME_COUNTER)),
    )

    assert isinstance(typ, types.UnionType)
    assert [type_str(item) for item in typ.items] == [
        f'{IntBox.__module__}.{IntBox.__qualname__}@1',
        f'{Box.__module__}.{Box.__qualname__}@2[builtins.str]',
    ]


def test_reflect_meet_returns_runtime_generic_subclass() -> None:
    t_var = ta.TypeVar('T')  # type: ignore

    class Box(ta.Generic[t_var]):  # type: ignore
        pass

    class IntBox(Box[int]):  # type: ignore
        pass

    typ = reflect_meet(
        IntBox,
        Box[int],  # type: ignore
        RuntimeTypeReflector(RuntimeTypeUniverse(dynamic_type_name_suffix=DYNAMIC_TYPE_NAME_COUNTER)),
    )

    assert isinstance(typ, types.Instance)
    assert typ.type.fullname.endswith('.IntBox@1')


def test_reflect_meet_with_different_runtime_generic_base_arg_returns_uninhabited() -> None:
    t_var = ta.TypeVar('T')  # type: ignore

    class Box(ta.Generic[t_var]):  # type: ignore
        pass

    class IntBox(Box[int]):  # type: ignore
        pass

    typ = reflect_meet(IntBox, Box[str], RuntimeTypeReflector(RuntimeTypeUniverse()))  # type: ignore

    assert isinstance(typ, types.UninhabitedType)


def test_reflect_join_flattens_runtime_union() -> None:
    typ = reflect_join(int | str, int, RuntimeTypeReflector(RuntimeTypeUniverse()))

    assert isinstance(typ, types.UnionType)
    assert [type_str(item) for item in typ.items] == ['builtins.int', 'builtins.str']


def test_reflect_join_keeps_invariant_runtime_generic_aliases() -> None:
    typ = reflect_join(list[int], list[str], RuntimeTypeReflector(RuntimeTypeUniverse()))

    assert isinstance(typ, types.UnionType)
    assert [type_str(item) for item in typ.items] == [
        'builtins.list[builtins.int]',
        'builtins.list[builtins.str]',
    ]


def test_reflect_join_synthesizes_fixed_tuple_itemwise_join() -> None:
    typ = reflect_join(
        tuple[int, object],
        tuple[object, str],
        RuntimeTypeReflector(RuntimeTypeUniverse()),
    )

    assert isinstance(typ, types.TupleType)
    assert type_str(typ) == 'tuple[builtins.object, builtins.object]'


def test_reflect_meet_synthesizes_fixed_tuple_itemwise_meet() -> None:
    typ = reflect_meet(
        tuple[int, object],
        tuple[object, str],
        RuntimeTypeReflector(RuntimeTypeUniverse()),
    )

    assert isinstance(typ, types.TupleType)
    assert type_str(typ) == 'tuple[builtins.int, builtins.str]'


def test_reflect_structural_join_expands_variadic_alias_to_fixed_tuple() -> None:
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    alias = ta.TypeAliasType('Alias', tuple[*ts_var], type_params=(ts_var,))  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    alias_type = reflector.reflect_type(alias[int, str])

    typ = reflect_structural_join(alias[int, str], tuple[int, str], reflector)

    assert typ is alias_type


def test_reflect_structural_meet_expands_variadic_alias_to_fixed_tuple() -> None:
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    alias = ta.TypeAliasType('Alias', tuple[*ts_var], type_params=(ts_var,))  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    alias_type = reflector.reflect_type(alias[int, str])

    typ = reflect_structural_meet(alias[int, str], tuple[int, str], reflector)

    assert typ is alias_type


def test_reflect_join_and_meet_fail_closed_for_variadic_tuple_shapes() -> None:
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    variadic = tuple[*ts_var]  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    with pytest.raises(UnsupportedTypeOperationError, match='variadic Tuple join'):
        reflect_join(variadic, tuple[int], reflector)

    with pytest.raises(UnsupportedTypeOperationError, match='variadic Tuple meet'):
        reflect_meet(tuple[int], variadic, reflector)


def test_reflect_meet_distributes_runtime_union_to_matching_item() -> None:
    typ = reflect_meet(int | str, int, RuntimeTypeReflector(RuntimeTypeUniverse()))

    assert isinstance(typ, types.Instance)
    assert typ.type.fullname == 'builtins.int'


def test_reflect_meet_distributes_runtime_union_to_uninhabited() -> None:
    typ = reflect_meet(int | str, float, RuntimeTypeReflector(RuntimeTypeUniverse()))

    assert isinstance(typ, types.UninhabitedType)


def test_reflect_join_builds_structural_typed_dict_join() -> None:
    class Left(ta.TypedDict):
        x: int
        left: str

    class Right(ta.TypedDict):
        x: int
        right: str

    typ = reflect_join(Left, Right, RuntimeTypeReflector(RuntimeTypeUniverse()))

    assert isinstance(typ, types.TypedDictType)
    assert type_str(typ) == "TypedDict({'x': builtins.int})"


def test_reflect_meet_builds_structural_typed_dict_meet() -> None:
    class Left(ta.TypedDict):
        x: int
        left: str

    class Right(ta.TypedDict):
        x: int
        right: str

    typ = reflect_meet(Left, Right, RuntimeTypeReflector(RuntimeTypeUniverse()))

    assert isinstance(typ, types.TypedDictType)
    assert typ.required_keys == {'x', 'left', 'right'}
    assert {name: type_str(item) for name, item in typ.items.items()} == {
        'x': 'builtins.int',
        'left': 'builtins.str',
        'right': 'builtins.str',
    }


def test_reflect_meet_rejects_incompatible_mutable_typed_dict_item() -> None:
    class Left(ta.TypedDict):
        x: int

    class Right(ta.TypedDict):
        x: str

    with pytest.raises(UnsupportedTypeOperationError):
        reflect_meet(Left, Right, RuntimeTypeReflector(RuntimeTypeUniverse()))


def test_reflect_structural_join_recursive_alias_matches_one_unrolling() -> None:
    alias = ta.TypeAliasType('Node', int | list['Node'])  # type: ignore
    unrolled = int | list[alias]  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    alias_type = reflector.reflect_type(alias)

    typ = reflect_structural_join(alias, unrolled, reflector)

    assert typ is alias_type


def test_reflect_structural_meet_recursive_alias_matches_one_unrolling() -> None:
    alias = ta.TypeAliasType('Node', int | list['Node'])  # type: ignore
    unrolled = int | list[alias]  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    alias_type = reflector.reflect_type(alias)

    typ = reflect_structural_meet(alias, unrolled, reflector)

    assert typ is alias_type


def test_reflect_structural_equivalence_variadic_recursive_alias_matches_one_unrolling() -> None:
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    alias = ta.TypeAliasType('TupleNode', tuple[*ts_var, 'TupleNode[*Ts]'], type_params=(ts_var,))  # type: ignore
    unrolled = tuple[int, str, alias[int, str]]  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse(), forward_ref_resolver={'TupleNode': alias}.__getitem__)

    assert reflect_is_structurally_equivalent(alias[int, str], unrolled, reflector)
    assert reflect_is_structurally_equivalent_or_false(alias[int, str], unrolled, reflector)


def test_reflect_structural_join_variadic_recursive_alias_matches_one_unrolling() -> None:
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    alias = ta.TypeAliasType('TupleNode', tuple[*ts_var, 'TupleNode[*Ts]'], type_params=(ts_var,))  # type: ignore
    unrolled = tuple[int, str, alias[int, str]]  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse(), forward_ref_resolver={'TupleNode': alias}.__getitem__)
    alias_type = reflector.reflect_type(alias[int, str])

    typ = reflect_structural_join(alias[int, str], unrolled, reflector)

    assert typ is alias_type


def test_reflect_structural_meet_variadic_recursive_alias_matches_one_unrolling() -> None:
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    alias = ta.TypeAliasType('TupleNode', tuple[*ts_var, 'TupleNode[*Ts]'], type_params=(ts_var,))  # type: ignore
    unrolled = tuple[int, str, alias[int, str]]  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse(), forward_ref_resolver={'TupleNode': alias}.__getitem__)
    alias_type = reflector.reflect_type(alias[int, str])

    typ = reflect_structural_meet(alias[int, str], unrolled, reflector)

    assert typ is alias_type


def test_reflect_structural_join_recursive_aliases_with_same_structure() -> None:
    left = ta.TypeAliasType('Left', int | list['Left'])  # type: ignore
    right = ta.TypeAliasType('Right', int | list['Right'])  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    left_type = reflector.reflect_type(left)

    typ = reflect_structural_join(left, right, reflector)

    assert typ is left_type


def test_reflect_structural_meet_recursive_aliases_with_same_structure() -> None:
    left = ta.TypeAliasType('Left', int | list['Left'])  # type: ignore
    right = ta.TypeAliasType('Right', int | list['Right'])  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    left_type = reflector.reflect_type(left)

    typ = reflect_structural_meet(left, right, reflector)

    assert typ is left_type


def test_reflect_structural_join_and_meet_recursive_alias_with_object_bound() -> None:
    alias = ta.TypeAliasType('Node', int | list['Node'])  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse(), forward_ref_resolver={'Node': alias}.__getitem__)
    alias_type = reflector.reflect_type(alias)

    joined = reflect_structural_join(alias, object, reflector)
    met = reflect_structural_meet(alias, object, reflector)

    assert type_str(joined) == 'builtins.object'
    assert met is alias_type


def test_reflect_structural_join_incompatible_recursive_aliases_returns_union() -> None:
    left = ta.TypeAliasType('Left', int | list['Left'])  # type: ignore
    right = ta.TypeAliasType('Right', str | list['Right'])  # type: ignore

    typ = reflect_structural_join(left, right, RuntimeTypeReflector(RuntimeTypeUniverse()))

    assert isinstance(typ, types.UnionType)
    assert [type_str(item).rsplit('.', 1)[-1] for item in typ.items] == ['Left', 'Right']


def test_reflect_structural_meet_incompatible_recursive_aliases_returns_uninhabited() -> None:
    left = ta.TypeAliasType('Left', int | list['Left'])  # type: ignore
    right = ta.TypeAliasType('Right', str | list['Right'])  # type: ignore

    typ = reflect_structural_meet(left, right, RuntimeTypeReflector(RuntimeTypeUniverse()))

    assert isinstance(typ, types.UninhabitedType)


def test_reflect_structural_join_list_folds_recursive_aliases() -> None:
    alias = ta.TypeAliasType('Node', int | list['Node'])  # type: ignore
    unrolled = int | list[alias]  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    alias_type = reflector.reflect_type(alias)

    typ = reflect_structural_join_list([alias, unrolled], reflector)

    assert typ is alias_type


def test_reflect_structural_meet_list_folds_recursive_aliases() -> None:
    alias = ta.TypeAliasType('Node', int | list['Node'])  # type: ignore
    unrolled = int | list[alias]  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    alias_type = reflector.reflect_type(alias)

    typ = reflect_structural_meet_list([alias, unrolled], reflector)

    assert typ is alias_type


def test_reflect_structural_join_list_folds_variadic_recursive_aliases() -> None:
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    alias = ta.TypeAliasType('TupleNode', tuple[*ts_var, 'TupleNode[*Ts]'], type_params=(ts_var,))  # type: ignore
    unrolled = tuple[int, str, alias[int, str]]  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse(), forward_ref_resolver={'TupleNode': alias}.__getitem__)
    alias_type = reflector.reflect_type(alias[int, str])

    typ = reflect_structural_join_list([alias[int, str], unrolled], reflector)

    assert typ is alias_type


def test_reflect_structural_meet_list_folds_variadic_recursive_aliases() -> None:
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    alias = ta.TypeAliasType('TupleNode', tuple[*ts_var, 'TupleNode[*Ts]'], type_params=(ts_var,))  # type: ignore
    unrolled = tuple[int, str, alias[int, str]]  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse(), forward_ref_resolver={'TupleNode': alias}.__getitem__)
    alias_type = reflector.reflect_type(alias[int, str])

    typ = reflect_structural_meet_list([alias[int, str], unrolled], reflector)

    assert typ is alias_type


def test_reflect_structural_ops_fail_closed_for_recursive_param_spec_callable_alias() -> None:
    param_spec = ta.ParamSpec('P')  # type: ignore
    alias = ta.TypeAliasType('Fn', ta.Callable[param_spec, 'Fn'])  # type: ignore

    with pytest.raises(UnsupportedTypeOperationError):
        reflect_structural_join(alias, ta.Callable[[int], int], RuntimeTypeReflector(RuntimeTypeUniverse()))

    with pytest.raises(UnsupportedTypeOperationError):
        reflect_structural_meet(alias, ta.Callable[[int], int], RuntimeTypeReflector(RuntimeTypeUniverse()))


def test_reflect_join_propagates_unsupported_core_operation() -> None:
    with pytest.raises(UnsupportedTypeOperationError):
        reflect_join(ta.Callable[..., int], object, RuntimeTypeReflector(RuntimeTypeUniverse()))


def test_reflect_meet_propagates_unsupported_core_operation() -> None:
    with pytest.raises(UnsupportedTypeOperationError):
        reflect_meet(ta.Callable[..., int], object, RuntimeTypeReflector(RuntimeTypeUniverse()))


def test_reflect_join_propagates_unreflectable_runtime_input() -> None:
    with pytest.raises(UnreflectableTypeError):
        reflect_join(object(), int, RuntimeTypeReflector(RuntimeTypeUniverse()))


def test_reflect_meet_propagates_unreflectable_runtime_input() -> None:
    with pytest.raises(UnreflectableTypeError):
        reflect_meet(object(), int, RuntimeTypeReflector(RuntimeTypeUniverse()))


def test_reflect_join_list_folds_runtime_type_objects() -> None:
    typ = reflect_join_list([int, str, int], RuntimeTypeReflector(RuntimeTypeUniverse()))

    assert isinstance(typ, types.UnionType)
    assert [type_str(item) for item in typ.items] == ['builtins.int', 'builtins.str']


def test_reflect_meet_list_folds_runtime_type_objects() -> None:
    typ = reflect_meet_list([int, object], RuntimeTypeReflector(RuntimeTypeUniverse()))

    assert isinstance(typ, types.Instance)
    assert typ.type.fullname == 'builtins.int'


def test_reflect_is_assignable_uses_runtime_nominal_subtyping() -> None:
    class Base:
        pass

    class Child(Base):
        pass

    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    assert reflect_is_assignable(Child, Base, reflector)
    assert not reflect_is_assignable(Base, Child, reflector)


def test_reflect_is_assignable_uses_runtime_generic_base_mapping() -> None:
    t_var = ta.TypeVar('T')  # type: ignore

    class Box(ta.Generic[t_var]):  # type: ignore
        pass

    class IntBox(Box[int]):  # type: ignore
        pass

    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    assert reflect_is_assignable(IntBox, Box[int], reflector)  # type: ignore
    assert not reflect_is_assignable(IntBox, Box[str], reflector)  # type: ignore


def test_reflect_is_assignable_uses_known_collection_abc_base_mapping() -> None:
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    assert reflect_is_assignable(list[int], cabc.Sequence[int], reflector)
    assert reflect_is_assignable(list[int], cabc.Iterable[int], reflector)
    assert not reflect_is_assignable(list[int], cabc.Sequence[str], reflector)
    assert reflect_is_assignable(str, cabc.Sequence[str], reflector)
    assert reflect_is_assignable(bytes, cabc.Sequence[int], reflector)
    assert not reflect_is_assignable(bytes, cabc.Sequence[str], reflector)
    assert reflect_is_assignable(tuple[int, ...], cabc.Sequence[int], reflector)
    assert reflect_is_assignable(dict[str, int], cabc.Mapping[str, int], reflector)
    assert reflect_is_assignable(set[int], cabc.Set[int], reflector)
    assert reflect_is_assignable(frozenset[int], cabc.Set[int], reflector)


def test_reflect_is_assignable_handles_runtime_unions() -> None:
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    assert reflect_is_assignable(int, int | str, reflector)
    assert not reflect_is_assignable(int | str, int, reflector)


def test_reflect_is_assignable_uses_typed_dict_structural_keys() -> None:
    class Source(ta.TypedDict):
        x: int
        extra: str

    class Target(ta.TypedDict):
        x: int

    class TargetWithOptional(ta.TypedDict):
        x: int
        maybe: ta.NotRequired[str]

    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    assert reflect_is_assignable(Source, Target, reflector)
    assert reflect_is_assignable(Source, TargetWithOptional, reflector)
    assert not reflect_is_assignable(Target, Source, reflector)


def test_reflect_is_assignable_requires_typed_dict_required_target_keys() -> None:
    class Source(ta.TypedDict, total=False):
        x: int

    class Target(ta.TypedDict):
        x: int

    assert not reflect_is_assignable(Source, Target, RuntimeTypeReflector(RuntimeTypeUniverse()))


def test_reflect_is_assignable_uses_typed_dict_readonly_covariance() -> None:
    class Base:
        pass

    class Child(Base):
        pass

    class Source(ta.TypedDict):
        x: Child

    class ReadOnlyTarget(ta.TypedDict):
        x: ta.ReadOnly[Base]

    class MutableTarget(ta.TypedDict):
        x: Base

    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    assert reflect_is_assignable(Source, ReadOnlyTarget, reflector)
    assert not reflect_is_assignable(Source, MutableTarget, reflector)


def test_reflect_is_assignable_rejects_readonly_typed_dict_source_for_mutable_target() -> None:
    class Source(ta.TypedDict):
        x: ta.ReadOnly[int]

    class Target(ta.TypedDict):
        x: int

    assert not reflect_is_assignable(Source, Target, RuntimeTypeReflector(RuntimeTypeUniverse()))


def test_reflect_is_same_type_matches_typing_union_and_pep604_union() -> None:
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    assert reflect_is_same_type(ta.Union[int, str], int | str, reflector)  # noqa


def test_reflect_is_same_type_matches_typing_optional_and_pep604_optional() -> None:
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    assert reflect_is_same_type(ta.Optional[int], int | None, reflector)  # noqa


def test_reflect_is_same_type_matches_never_and_no_return() -> None:
    assert reflect_is_same_type(ta.Never, ta.NoReturn, RuntimeTypeReflector(RuntimeTypeUniverse()))


def test_reflect_is_assignable_keeps_any_compatibility() -> None:
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    assert reflect_is_assignable(ta.Any, int, reflector)
    assert reflect_is_assignable(int, ta.Any, reflector)


def test_reflect_is_assignable_treats_never_as_bottom() -> None:
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    assert reflect_is_assignable(ta.Never, int, reflector)
    assert not reflect_is_assignable(int, ta.Never, reflector)


def test_reflect_is_assignable_supports_simple_callable_variance() -> None:
    class Base:
        pass

    class Child(Base):
        pass

    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    assert reflect_is_assignable(
        cabc.Callable[[Base], Child],
        cabc.Callable[[Child], Base],
        reflector,
    )
    assert not reflect_is_assignable(
        cabc.Callable[[Child], Base],
        cabc.Callable[[Base], Child],
        reflector,
    )


def test_reflect_is_assignable_supports_callable_ellipsis_return_covariance() -> None:
    class Base:
        pass

    class Child(Base):
        pass

    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    assert reflect_is_assignable(cabc.Callable[..., Child], cabc.Callable[..., Base], reflector)
    assert not reflect_is_assignable(cabc.Callable[..., Base], cabc.Callable[..., Child], reflector)


def test_reflect_is_assignable_or_false_suppresses_generic_callable_subtyping() -> None:
    param_spec = ta.ParamSpec('P')  # type: ignore

    assert not reflect_is_assignable_or_false(
        cabc.Callable[param_spec, int],
        cabc.Callable[param_spec, object],
        RuntimeTypeReflector(RuntimeTypeUniverse()),
    )


def test_reflect_is_assignable_raises_for_unsupported_core_operation() -> None:
    with pytest.raises(UnsupportedTypeOperationError):
        reflect_is_assignable(ta.Callable[..., int], object, RuntimeTypeReflector(RuntimeTypeUniverse()))


def test_reflect_is_assignable_or_false_is_conservative() -> None:
    assert not reflect_is_assignable_or_false(
        ta.Callable[..., int],
        object,
        RuntimeTypeReflector(RuntimeTypeUniverse()),
    )


def test_reflect_is_same_type_matches_same_runtime_type_var() -> None:
    t_var = ta.TypeVar('T')  # type: ignore

    assert reflect_is_same_type(
        list[t_var],  # type: ignore
        list[t_var],  # type: ignore
        RuntimeTypeReflector(RuntimeTypeUniverse()),
    )


def test_reflect_is_same_type_keeps_same_name_type_vars_distinct() -> None:
    left = ta.TypeVar('T')  # type: ignore
    right = ta.TypeVar('T')  # type: ignore

    assert not reflect_is_same_type(
        list[left],  # type: ignore
        list[right],  # type: ignore
        RuntimeTypeReflector(RuntimeTypeUniverse()),
    )


def test_reflect_is_alpha_equivalent_allows_same_shape_type_vars() -> None:
    left = ta.TypeVar('T')  # type: ignore
    right = ta.TypeVar('U')  # type: ignore

    assert reflect_is_alpha_equivalent(
        dict[str, left],  # type: ignore
        dict[str, right],  # type: ignore
        RuntimeTypeReflector(RuntimeTypeUniverse()),
    )


def test_reflect_is_alpha_equivalent_rejects_different_type_shape() -> None:
    left = ta.TypeVar('T')  # type: ignore
    right = ta.TypeVar('U')  # type: ignore

    assert not reflect_is_alpha_equivalent(
        dict[str, left],  # type: ignore
        list[right],  # type: ignore
        RuntimeTypeReflector(RuntimeTypeUniverse()),
    )


def test_reflect_comparison_propagates_unreflectable_runtime_input() -> None:
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    with pytest.raises(UnreflectableTypeError):
        reflect_is_same_type(object(), int, reflector)

    with pytest.raises(UnreflectableTypeError):
        reflect_is_alpha_equivalent(object(), int, reflector)


def test_reflect_comparison_rejects_self_without_class_context() -> None:
    with pytest.raises(UnreflectableTypeError):
        reflect_is_same_type(ta.Self, ta.Self, RuntimeTypeReflector(RuntimeTypeUniverse()))


def test_reflect_type_str_formats_runtime_generic_alias() -> None:
    assert reflect_type_str(list[int], RuntimeTypeReflector(RuntimeTypeUniverse())) == 'builtins.list[builtins.int]'


def test_reflect_type_str_formats_runtime_union() -> None:
    assert reflect_type_str(int | None, RuntimeTypeReflector(RuntimeTypeUniverse())) == 'Union[builtins.int, None]'


def test_reflect_type_str_formats_never() -> None:
    assert reflect_type_str(ta.Never, RuntimeTypeReflector(RuntimeTypeUniverse())) == 'Never'
    assert reflect_type_str(ta.NoReturn, RuntimeTypeReflector(RuntimeTypeUniverse())) == 'Never'


def test_reflect_type_str_formats_type_guard_as_guarded_type() -> None:
    assert reflect_type_str(ta.TypeGuard[int], RuntimeTypeReflector(RuntimeTypeUniverse())) == 'builtins.int'


def test_reflect_type_str_formats_typed_dict_wrappers() -> None:
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    assert reflect_type_str(ta.Required[int], reflector) == 'Required[builtins.int]'
    assert reflect_type_str(ta.NotRequired[str], reflector) == 'NotRequired[builtins.str]'
    assert reflect_type_str(ta.ReadOnly[bool], reflector) == 'ReadOnly[builtins.bool]'


def test_reflect_type_str_formats_unpack() -> None:
    assert reflect_type_str(
        ta.Unpack[tuple[int, str]],
        RuntimeTypeReflector(RuntimeTypeUniverse()),
    ) == 'Unpack[tuple[builtins.int, builtins.str]]'


def test_reflect_type_str_formats_unpack_of_type_var_tuple() -> None:
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore

    assert reflect_type_str(
        ta.Unpack[ts_var],
        RuntimeTypeReflector(RuntimeTypeUniverse()),
    ) == 'Unpack[Ts]'


def test_reflect_type_str_formats_typed_dict_class() -> None:
    class Movie(ta.TypedDict, total=False):
        title: ta.Required[str]
        year: int
        tag: ta.ReadOnly[ta.NotRequired[str]]

    assert reflect_type_str(Movie, RuntimeTypeReflector(RuntimeTypeUniverse())) == (
        "TypedDict({'title': builtins.str, 'year'?: builtins.int, 'tag'?=: builtins.str})"
    )


def test_reflect_is_same_type_unwraps_type_guarded_type() -> None:
    assert reflect_is_same_type(ta.TypeGuard[int], int, RuntimeTypeReflector(RuntimeTypeUniverse()))


def test_reflect_is_same_type_distinguishes_required_from_not_required() -> None:
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    assert reflect_is_same_type(ta.Required[int], ta.Required[int], reflector)
    assert reflect_is_same_type(ta.NotRequired[int], ta.NotRequired[int], reflector)
    assert not reflect_is_same_type(ta.Required[int], ta.NotRequired[int], reflector)


def test_reflect_is_same_type_compares_unpack() -> None:
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    assert reflect_is_same_type(ta.Unpack[tuple[int, str]], ta.Unpack[tuple[int, str]], reflector)
    assert not reflect_is_same_type(ta.Unpack[tuple[int]], ta.Unpack[tuple[str]], reflector)


def test_reflect_is_same_type_compares_typed_dict_classes() -> None:
    class Left(ta.TypedDict):
        x: int

    class Right(ta.TypedDict):
        x: int

    class OptionalRight(ta.TypedDict, total=False):
        x: int

    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    assert reflect_is_same_type(Left, Right, reflector)
    assert not reflect_is_same_type(Left, OptionalRight, reflector)


def test_reflect_type_str_rejects_type_is_until_distinct_representation_exists() -> None:
    with pytest.raises(UnreflectableTypeError, match='TypeIs'):
        reflect_type_str(ta.TypeIs[int], RuntimeTypeReflector(RuntimeTypeUniverse()))


def test_reflect_type_str_formats_type_alias_type_value() -> None:
    alias = ta.TypeAliasType('Alias', list[int])  # type: ignore

    assert reflect_type_str(alias, RuntimeTypeReflector(RuntimeTypeUniverse())) == f'{__name__}.Alias'
    assert type_str(get_proper_type(RuntimeTypeReflector(RuntimeTypeUniverse()).reflect_type(alias))) == (
        'builtins.list[builtins.int]'
    )


def test_reflect_is_same_type_matches_type_alias_type_value() -> None:
    alias = ta.TypeAliasType('Alias', list[int])  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    assert not reflect_is_same_type(alias, list[int], reflector)
    assert reflect_runtime_effective_type_key(alias, reflector) == reflect_runtime_effective_type_key(
        list[int],
        reflector,
    )


def test_reflect_type_str_formats_subscripted_type_alias_type_value() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    alias = ta.TypeAliasType('Alias', list[t_var], type_params=(t_var,))  # type: ignore

    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    assert reflect_type_str(alias[str], reflector) == f'{__name__}.Alias[builtins.str]'
    assert type_str(get_proper_type(reflector.reflect_type(alias[str]))) == 'builtins.list[builtins.str]'


def test_reflect_type_str_formats_typing_optional_like_pep604_optional() -> None:
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    assert reflect_type_str(ta.Optional[int], reflector) == reflect_type_str(int | None, reflector)  # noqa


def test_reflect_type_str_formats_typing_union_like_pep604_union() -> None:
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    assert reflect_type_str(ta.Union[int, str], reflector) == reflect_type_str(int | str, reflector)  # noqa


def test_reflect_type_str_rejects_self_without_class_context() -> None:
    with pytest.raises(UnreflectableTypeError):
        reflect_type_str(ta.Self, RuntimeTypeReflector(RuntimeTypeUniverse()))


def test_reflect_type_str_uses_explicit_forward_ref_resolver() -> None:
    reflector = RuntimeTypeReflector(
        RuntimeTypeUniverse(),
        forward_ref_resolver=lambda name: {'User': int}[name],
    )

    assert reflect_type_str('User', reflector) == 'builtins.int'


def test_reflect_type_str_without_forward_ref_resolver_still_rejects_forward_ref() -> None:
    with pytest.raises(UnreflectableTypeError, match='forward reference'):
        reflect_type_str('User', RuntimeTypeReflector(RuntimeTypeUniverse()))


def test_reflect_is_same_type_uses_explicit_forward_ref_resolver() -> None:
    reflector = RuntimeTypeReflector(
        RuntimeTypeUniverse(),
        forward_ref_resolver=lambda name: {'User': int}[name],
    )

    assert reflect_is_same_type('User', int, reflector)


def test_reflect_type_strs_formats_runtime_types() -> None:
    assert reflect_type_strs([int, str], RuntimeTypeReflector(RuntimeTypeUniverse())) == [
        'builtins.int',
        'builtins.str',
    ]


def test_reflect_literal_values_returns_single_runtime_literal_value() -> None:
    assert reflect_literal_values(ta.Literal['x'], RuntimeTypeReflector(RuntimeTypeUniverse())) == ['x']


def test_reflect_literal_values_returns_multi_literal_values_in_order() -> None:
    assert reflect_literal_values(
        ta.Literal['x', 1, False, b'y', 1.5, None],
        RuntimeTypeReflector(RuntimeTypeUniverse()),
    ) == [
        'x',
        1,
        False,
        b'y',
        1.5,
        None,
    ]


def test_reflect_literal_values_returns_bytes_literal_values() -> None:
    assert reflect_literal_values(
        ta.Literal[b'x', b'y'],
        RuntimeTypeReflector(RuntimeTypeUniverse()),
    ) == [
        b'x',
        b'y',
    ]


def test_reflect_literal_values_returns_union_literal_values_in_order() -> None:
    assert reflect_literal_values(
        ta.Literal['x'] | ta.Literal[1],  # noqa
        RuntimeTypeReflector(RuntimeTypeUniverse()),
    ) == [
        'x',
        1,
    ]


def test_reflect_literal_values_or_none_returns_none_for_non_literal_type() -> None:
    assert reflect_literal_values_or_none(str, RuntimeTypeReflector(RuntimeTypeUniverse())) is None


def test_reflect_literal_values_or_none_returns_none_for_mixed_union() -> None:
    assert reflect_literal_values_or_none(
        ta.Literal['x'] | str,  # noqa
        RuntimeTypeReflector(RuntimeTypeUniverse()),
    ) is None


def test_reflect_literal_values_raises_for_non_finite_literal_set() -> None:
    with pytest.raises(ReflectionError, match='finite literal'):
        reflect_literal_values(str, RuntimeTypeReflector(RuntimeTypeUniverse()))


def test_reflect_typed_dict_literal_values_returns_per_item_literal_values() -> None:
    class Message(ta.TypedDict):
        kind: ta.Literal['create', 'delete']
        id: int

    assert reflect_typed_dict_literal_values(Message, RuntimeTypeReflector(RuntimeTypeUniverse())) == {
        'kind': ['create', 'delete'],
        'id': None,
    }


def test_reflect_typed_dict_literal_values_keeps_optional_and_readonly_items() -> None:
    class Message(ta.TypedDict, total=False):
        kind: ta.Required[ta.Literal['create']]
        mode: ta.ReadOnly[ta.NotRequired[ta.Literal['dry-run', 'commit']]]
        id: int

    assert reflect_typed_dict_literal_values(Message, RuntimeTypeReflector(RuntimeTypeUniverse())) == {
        'kind': ['create'],
        'mode': ['dry-run', 'commit'],
        'id': None,
    }


def test_reflect_typed_dict_literal_values_returns_none_for_mixed_literal_item() -> None:
    class Message(ta.TypedDict):
        kind: ta.Literal['create'] | str  # noqa

    assert reflect_typed_dict_literal_values(Message, RuntimeTypeReflector(RuntimeTypeUniverse())) == {
        'kind': None,
    }


def test_reflect_typed_dict_literal_values_uses_explicit_forward_ref_resolver() -> None:
    class Message(ta.TypedDict):
        value: 'Value'  # type: ignore  # noqa

    reflector = RuntimeTypeReflector(
        RuntimeTypeUniverse(),
        forward_ref_resolver=lambda name: {'Value': ta.Literal['x', 'y']}[name],
    )

    assert reflect_typed_dict_literal_values(Message, reflector) == {
        'value': ['x', 'y'],
    }


def test_reflect_typed_dict_literal_values_rejects_non_typed_dict_type() -> None:
    with pytest.raises(ReflectionError, match='TypedDict'):
        reflect_typed_dict_literal_values(str, RuntimeTypeReflector(RuntimeTypeUniverse()))


def test_reflect_type_str_reuses_explicit_reflector() -> None:
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    assert reflect_type_str(list[int], reflector) == type_str(reflector.reflect_type(list[int]))


def test_reflect_instance_returns_runtime_instance_type() -> None:
    typ = reflect_instance(list[int], RuntimeTypeReflector(RuntimeTypeUniverse()))

    assert isinstance(typ, types.Instance)
    assert typ.type.fullname == 'builtins.list'
    assert [type_str(arg) for arg in typ.args] == ['builtins.int']


def test_reflect_instance_info_returns_type_info() -> None:
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    assert reflect_instance_info(dict[str, int], reflector) is reflect_instance(dict[str, int], reflector).type
    assert reflect_instance_info(dict[str, int], reflector).fullname == 'builtins.dict'


def test_reflect_instance_args_returns_instance_args() -> None:
    args = reflect_instance_args(dict[str, int], RuntimeTypeReflector(RuntimeTypeUniverse()))

    assert [type_str(arg) for arg in args] == ['builtins.str', 'builtins.int']


def test_reflect_instance_uses_explicit_dynamic_name_mode() -> None:
    class Local:
        pass

    typ = reflect_instance(
        Local,
        RuntimeTypeReflector(RuntimeTypeUniverse(dynamic_type_name_suffix=DYNAMIC_TYPE_NAME_COUNTER)),
    )

    assert typ.type.fullname.endswith('.Local@1')


def test_reflect_instance_rejects_non_instance_runtime_type() -> None:
    with pytest.raises(ReflectionError, match='instance type'):
        reflect_instance(int | str, RuntimeTypeReflector(RuntimeTypeUniverse()))

    with pytest.raises(ReflectionError, match='instance type'):
        reflect_instance(ta.Callable[..., int], RuntimeTypeReflector(RuntimeTypeUniverse()))


def test_reflect_base_args_returns_args_for_bare_runtime_generic_base() -> None:
    t_var = ta.TypeVar('T')  # type: ignore

    class Box(ta.Generic[t_var]):  # type: ignore
        pass

    class IntBox(Box[int]):  # type: ignore
        pass

    args = reflect_base_args(IntBox, Box, RuntimeTypeReflector(RuntimeTypeUniverse()))

    assert args is not None
    assert [type_str(arg) for arg in args] == ['builtins.int']


def test_reflect_base_args_returns_args_for_known_collection_abc_base() -> None:
    args = reflect_base_args(list[int], cabc.Sequence, RuntimeTypeReflector(RuntimeTypeUniverse()))

    assert args is not None
    assert [type_str(arg) for arg in args] == ['builtins.int']


def test_reflect_base_args_returns_args_for_str_sequence_base() -> None:
    args = reflect_base_args(str, cabc.Sequence, RuntimeTypeReflector(RuntimeTypeUniverse()))

    assert args is not None
    assert [type_str(arg) for arg in args] == ['builtins.str']


def test_reflect_base_args_returns_args_for_bytes_sequence_base() -> None:
    args = reflect_base_args(bytes, cabc.Sequence, RuntimeTypeReflector(RuntimeTypeUniverse()))

    assert args is not None
    assert [type_str(arg) for arg in args] == ['builtins.int']


def test_reflect_base_args_returns_args_for_indirect_known_collection_abc_base() -> None:
    args = reflect_base_args(list[int], cabc.Iterable, RuntimeTypeReflector(RuntimeTypeUniverse()))

    assert args is not None
    assert [type_str(arg) for arg in args] == ['builtins.int']


def test_reflect_base_args_returns_args_for_tuple_sequence_base() -> None:
    args = reflect_base_args(tuple[int, ...], cabc.Sequence, RuntimeTypeReflector(RuntimeTypeUniverse()))

    assert args is not None
    assert [type_str(arg) for arg in args] == ['builtins.int']


def test_reflect_base_args_returns_args_for_dict_mapping_base() -> None:
    args = reflect_base_args(dict[str, int], cabc.Mapping, RuntimeTypeReflector(RuntimeTypeUniverse()))

    assert args is not None
    assert [type_str(arg) for arg in args] == ['builtins.str', 'builtins.int']


def test_reflect_base_args_returns_args_for_set_base() -> None:
    args = reflect_base_args(set[int], cabc.Set, RuntimeTypeReflector(RuntimeTypeUniverse()))

    assert args is not None
    assert [type_str(arg) for arg in args] == ['builtins.int']


def test_reflect_base_args_returns_args_for_frozenset_base() -> None:
    args = reflect_base_args(frozenset[int], cabc.Set, RuntimeTypeReflector(RuntimeTypeUniverse()))

    assert args is not None
    assert [type_str(arg) for arg in args] == ['builtins.int']


def test_reflect_base_args_returns_args_for_parameterized_runtime_generic_base() -> None:
    t_var = ta.TypeVar('T')  # type: ignore

    class Box(ta.Generic[t_var]):  # type: ignore
        pass

    class IntBox(Box[int]):  # type: ignore
        pass

    args = reflect_base_args(IntBox, Box[str], RuntimeTypeReflector(RuntimeTypeUniverse()))  # type: ignore

    assert args is not None
    assert [type_str(arg) for arg in args] == ['builtins.int']


def test_reflect_base_args_returns_args_through_indirect_runtime_generic_base() -> None:
    t_var = ta.TypeVar('T')  # type: ignore

    class Box(ta.Generic[t_var]):  # type: ignore
        pass

    class Middle(Box[t_var]):  # type: ignore
        pass

    class Child(Middle[int]):  # type: ignore
        pass

    args = reflect_base_args(Child, Box, RuntimeTypeReflector(RuntimeTypeUniverse()))

    assert args is not None
    assert [type_str(arg) for arg in args] == ['builtins.int']


def test_reflect_base_args_returns_none_for_missing_runtime_base() -> None:
    t_var = ta.TypeVar('T')  # type: ignore

    class Box(ta.Generic[t_var]):  # type: ignore
        pass

    class Other:
        pass

    assert reflect_base_args(Other, Box, RuntimeTypeReflector(RuntimeTypeUniverse())) is None


def test_reflect_base_args_rejects_non_instance_runtime_target() -> None:
    with pytest.raises(ReflectionError, match='base target'):
        reflect_base_args(list[int], int | str, RuntimeTypeReflector(RuntimeTypeUniverse()))


def test_reflect_base_args_or_none_returns_args_when_mappable() -> None:
    t_var = ta.TypeVar('T')  # type: ignore

    class Box(ta.Generic[t_var]):  # type: ignore
        pass

    class IntBox(Box[int]):  # type: ignore
        pass

    args = reflect_base_args_or_none(IntBox, Box, RuntimeTypeReflector(RuntimeTypeUniverse()))

    assert args is not None
    assert [type_str(arg) for arg in args] == ['builtins.int']


def test_reflect_base_args_or_none_returns_none_for_missing_runtime_base() -> None:
    t_var = ta.TypeVar('T')  # type: ignore

    class Box(ta.Generic[t_var]):  # type: ignore
        pass

    class Other:
        pass

    assert reflect_base_args_or_none(Other, Box, RuntimeTypeReflector(RuntimeTypeUniverse())) is None


def test_reflect_base_args_or_none_suppresses_unsupported_base_mapping() -> None:
    t_var = ta.TypeVar('T')  # type: ignore

    class Base(ta.Generic[t_var]):  # type: ignore
        pass

    class Middle:
        pass

    class Child(Middle):
        pass

    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    child_type = reflector.reflect_type(Child)
    base_type = reflector.reflect_type(Base)
    middle_type = reflector.reflect_type(Middle)
    assert isinstance(child_type, types.Instance)
    assert isinstance(base_type, types.Instance)
    assert isinstance(middle_type, types.Instance)
    child_type.type._mro = [child_type.type, middle_type.type, base_type.type]

    assert reflect_base_args_or_none(Child, Base, reflector) is None


def test_reflect_base_args_or_none_still_rejects_non_instance_runtime_target() -> None:
    with pytest.raises(ReflectionError, match='base target'):
        reflect_base_args_or_none(list[int], int | str, RuntimeTypeReflector(RuntimeTypeUniverse()))


def test_reflect_base_instance_returns_known_collection_abc_base() -> None:
    base = reflect_base_instance(list[int], cabc.Sequence, RuntimeTypeReflector(RuntimeTypeUniverse()))

    assert isinstance(base, types.Instance)
    assert base.type.fullname == 'collections.abc.Sequence'
    assert [type_str(arg) for arg in base.args] == ['builtins.int']


def test_reflect_base_instance_returns_mapping_base() -> None:
    base = reflect_base_instance(dict[str, int], cabc.Mapping, RuntimeTypeReflector(RuntimeTypeUniverse()))

    assert isinstance(base, types.Instance)
    assert base.type.fullname == 'collections.abc.Mapping'
    assert [type_str(arg) for arg in base.args] == ['builtins.str', 'builtins.int']


def test_reflect_base_instance_returns_none_for_missing_runtime_base() -> None:
    t_var = ta.TypeVar('T')  # type: ignore

    class Box(ta.Generic[t_var]):  # type: ignore
        pass

    class Other:
        pass

    assert reflect_base_instance(Other, Box, RuntimeTypeReflector(RuntimeTypeUniverse())) is None


def test_reflect_base_instance_or_none_suppresses_unsupported_base_mapping() -> None:
    t_var = ta.TypeVar('T')  # type: ignore

    class Base(ta.Generic[t_var]):  # type: ignore
        pass

    class Middle:
        pass

    class Child(Middle):
        pass

    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    child_type = reflector.reflect_type(Child)
    base_type = reflector.reflect_type(Base)
    middle_type = reflector.reflect_type(Middle)
    assert isinstance(child_type, types.Instance)
    assert isinstance(base_type, types.Instance)
    assert isinstance(middle_type, types.Instance)
    child_type.type._mro = [child_type.type, middle_type.type, base_type.type]

    with pytest.raises(UnsupportedTypeOperationError):
        reflect_base_instance(Child, Base, reflector)
    assert reflect_base_instance_or_none(Child, Base, reflector) is None


def test_reflect_base_instance_or_none_still_rejects_non_instance_runtime_target() -> None:
    with pytest.raises(ReflectionError, match='base target'):
        reflect_base_instance_or_none(list[int], int | str, RuntimeTypeReflector(RuntimeTypeUniverse()))


def test_reflect_mro_instances_remaps_type_vars_at_each_layer() -> None:
    a_var = ta.TypeVar('A')  # type: ignore
    b_var = ta.TypeVar('B')  # type: ignore
    x_var = ta.TypeVar('X')  # type: ignore
    y_var = ta.TypeVar('Y')  # type: ignore

    class Base(ta.Generic[a_var, b_var]):  # type: ignore
        pass

    class Middle(ta.Generic[x_var], Base[list[x_var], str]):  # type: ignore
        pass

    class Child(ta.Generic[y_var], Middle[dict[str, y_var]]):  # type: ignore
        pass

    mro = reflect_mro_instances(
        Child[int],  # type: ignore
        RuntimeTypeReflector(RuntimeTypeUniverse(dynamic_type_name_suffix=DYNAMIC_TYPE_NAME_COUNTER)),
    )

    assert [type_str(item) for item in mro] == [
        f'{Child.__module__}.{Child.__qualname__}@1[builtins.int]',
        f'{Middle.__module__}.{Middle.__qualname__}@2[builtins.dict[builtins.str, builtins.int]]',
        (
            f'{Base.__module__}.{Base.__qualname__}@3'
            '[builtins.list[builtins.dict[builtins.str, builtins.int]], builtins.str]'
        ),
        'typing.Generic',
        'builtins.object',
    ]


def test_reflect_mro_instances_rejects_non_instance_runtime_source() -> None:
    with pytest.raises(ReflectionError, match='MRO source'):
        reflect_mro_instances(int | str, RuntimeTypeReflector(RuntimeTypeUniverse()))


def test_reflect_mro_instances_or_none_returns_mapped_instances() -> None:
    t_var = ta.TypeVar('T')  # type: ignore

    class Box(ta.Generic[t_var]):  # type: ignore
        pass

    class IntBox(Box[int]):  # type: ignore
        pass

    mro = reflect_mro_instances_or_none(
        IntBox,
        RuntimeTypeReflector(RuntimeTypeUniverse(dynamic_type_name_suffix=DYNAMIC_TYPE_NAME_COUNTER)),
    )

    assert mro is not None
    assert [type_str(item) for item in mro] == [
        f'{IntBox.__module__}.{IntBox.__qualname__}@1',
        f'{Box.__module__}.{Box.__qualname__}@2[builtins.int]',
        'typing.Generic',
        'builtins.object',
    ]


def test_reflect_mro_instances_or_none_suppresses_unsupported_mapping() -> None:
    t_var = ta.TypeVar('T')  # type: ignore

    class Base(ta.Generic[t_var]):  # type: ignore
        pass

    class Middle:
        pass

    class Child(Middle):
        pass

    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    child_type = reflector.reflect_type(Child)
    base_type = reflector.reflect_type(Base)
    middle_type = reflector.reflect_type(Middle)
    assert isinstance(child_type, types.Instance)
    assert isinstance(base_type, types.Instance)
    assert isinstance(middle_type, types.Instance)
    child_type.type._mro = [child_type.type, middle_type.type, base_type.type]

    assert reflect_mro_instances_or_none(Child, reflector) is None


def test_reflect_mro_instances_or_none_still_rejects_non_instance_runtime_source() -> None:
    with pytest.raises(ReflectionError, match='MRO source'):
        reflect_mro_instances_or_none(int | str, RuntimeTypeReflector(RuntimeTypeUniverse()))


def test_reflect_mro_entries_exposes_info_instance_and_args() -> None:
    t_var = ta.TypeVar('T')  # type: ignore

    class Box(ta.Generic[t_var]):  # type: ignore
        pass

    class IntBox(Box[int]):  # type: ignore
        pass

    entries = reflect_mro_entries(
        IntBox,
        RuntimeTypeReflector(RuntimeTypeUniverse(dynamic_type_name_suffix=DYNAMIC_TYPE_NAME_COUNTER)),
    )

    assert [entry.info.fullname for entry in entries] == [
        f'{IntBox.__module__}.{IntBox.__qualname__}@1',
        f'{Box.__module__}.{Box.__qualname__}@2',
        'typing.Generic',
        'builtins.object',
    ]
    assert [type_str(entry.instance) for entry in entries] == [
        f'{IntBox.__module__}.{IntBox.__qualname__}@1',
        f'{Box.__module__}.{Box.__qualname__}@2[builtins.int]',
        'typing.Generic',
        'builtins.object',
    ]
    assert [[type_str(arg) for arg in entry.args] for entry in entries] == [
        [],
        ['builtins.int'],
        [],
        [],
    ]


def test_reflect_mro_entries_structural_keys_handle_recursive_alias_remapping() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    alias = ta.TypeAliasType('Node', int | list['Node'])  # type: ignore

    class Base(ta.Generic[t_var]):  # type: ignore
        pass

    class Middle(ta.Generic[t_var], Base[list[t_var]]):  # type: ignore
        pass

    class Child(Middle[alias]):  # type: ignore
        pass

    reflector = RuntimeTypeReflector(
        RuntimeTypeUniverse(dynamic_type_name_suffix=DYNAMIC_TYPE_NAME_COUNTER),
        forward_ref_resolver={'Node': alias}.__getitem__,
    )
    entries = reflect_mro_entries(Child, reflector)
    entries_by_name = {entry.info.name.split('@', 1)[0]: entry for entry in entries}
    alias_unrolled = reflector.reflect_type(int | list[alias])  # type: ignore
    list_unrolled = reflector.reflect_type(list[int | list[alias]])  # type: ignore

    assert [entry.info.name.split('@', 1)[0] for entry in entries[:3]] == ['Child', 'Middle', 'Base']
    assert [type_str(arg) for arg in entries_by_name['Middle'].args] == [
        f'{alias.__module__}.{alias.__name__}',
    ]
    assert [type_str(arg) for arg in entries_by_name['Base'].args] == [
        f'builtins.list[{alias.__module__}.{alias.__name__}]',
    ]
    assert reflector.structural_type_key(entries_by_name['Middle'].args[0]) == (
        reflector.structural_type_key(alias_unrolled)
    )
    assert reflector.structural_type_key(entries_by_name['Base'].args[0]) == (
        reflector.structural_type_key(list_unrolled)
    )


def test_reflect_mro_entries_or_none_suppresses_unsupported_mapping() -> None:
    t_var = ta.TypeVar('T')  # type: ignore

    class Base(ta.Generic[t_var]):  # type: ignore
        pass

    class Child:
        pass

    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    child_type = reflector.reflect_type(Child)
    base_type = reflector.reflect_type(Base)
    assert isinstance(child_type, types.Instance)
    assert isinstance(base_type, types.Instance)
    child_type.type._mro = [child_type.type, base_type.type]

    assert reflect_mro_entries_or_none(Child, reflector) is None


def test_reflect_mro_entries_still_rejects_non_instance_runtime_source() -> None:
    with pytest.raises(ReflectionError, match='MRO source'):
        reflect_mro_entries(int | str, RuntimeTypeReflector(RuntimeTypeUniverse()))


def test_reflect_mro_type_strs_formats_mapped_mro_instances() -> None:
    a_var = ta.TypeVar('A')  # type: ignore
    b_var = ta.TypeVar('B')  # type: ignore
    x_var = ta.TypeVar('X')  # type: ignore
    y_var = ta.TypeVar('Y')  # type: ignore

    class Base(ta.Generic[a_var, b_var]):  # type: ignore
        pass

    class Middle(ta.Generic[x_var], Base[list[x_var], str]):  # type: ignore
        pass

    class Child(ta.Generic[y_var], Middle[dict[str, y_var]]):  # type: ignore
        pass

    assert reflect_mro_type_strs(
        Child[int],  # type: ignore
        RuntimeTypeReflector(RuntimeTypeUniverse(dynamic_type_name_suffix=DYNAMIC_TYPE_NAME_COUNTER)),
    ) == [
        f'{Child.__module__}.{Child.__qualname__}@1[builtins.int]',
        f'{Middle.__module__}.{Middle.__qualname__}@2[builtins.dict[builtins.str, builtins.int]]',
        (
            f'{Base.__module__}.{Base.__qualname__}@3'
            '[builtins.list[builtins.dict[builtins.str, builtins.int]], builtins.str]'
        ),
        'typing.Generic',
        'builtins.object',
    ]


def test_reflect_mro_type_strs_rejects_non_instance_runtime_source() -> None:
    with pytest.raises(ReflectionError, match='MRO source'):
        reflect_mro_type_strs(int | str, RuntimeTypeReflector(RuntimeTypeUniverse()))


def test_reflect_ops_reuse_explicit_reflector() -> None:
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    left = reflect_join(list[int], list[int], reflector)
    right = reflector.reflect_type(list[int])

    assert left is right


def test_reflect_substitute_type_uses_runtime_type_var_keys() -> None:
    t_var = ta.TypeVar('T')  # type: ignore

    typ = reflect_substitute_type(
        list[t_var],  # type: ignore
        {t_var: int},
        RuntimeTypeReflector(RuntimeTypeUniverse()),
    )

    assert type_str(typ) == 'builtins.list[builtins.int]'


def test_reflect_substitute_type_uses_explicit_forward_ref_resolver() -> None:
    reflector = RuntimeTypeReflector(
        RuntimeTypeUniverse(),
        forward_ref_resolver=lambda name: {'User': int}[name],
    )

    typ = reflect_substitute_type(list['User'], {}, reflector)  # type: ignore

    assert type_str(typ) == 'builtins.list[builtins.int]'


def test_reflect_substitute_type_rejects_non_type_var_runtime_key() -> None:
    with pytest.raises(ReflectionError, match='substitution key'):
        reflect_substitute_type(list[int], {int: str}, RuntimeTypeReflector(RuntimeTypeUniverse()))


def test_reflect_substitute_types_uses_shared_runtime_type_var_key() -> None:
    t_var = ta.TypeVar('T')  # type: ignore

    typs = reflect_substitute_types(
        [list[t_var], dict[str, t_var]],  # type: ignore
        {t_var: int},
        RuntimeTypeReflector(RuntimeTypeUniverse()),
    )

    assert [type_str(typ) for typ in typs] == [
        'builtins.list[builtins.int]',
        'builtins.dict[builtins.str, builtins.int]',
    ]


def test_reflect_substitute_type_handles_runtime_abc_alias() -> None:
    t_var = ta.TypeVar('T')  # type: ignore

    typ = reflect_substitute_type(
        cabc.Sequence[t_var],  # type: ignore
        {t_var: str},
        RuntimeTypeReflector(RuntimeTypeUniverse()),
    )

    assert type_str(typ) == 'collections.abc.Sequence[builtins.str]'


def test_reflect_substitute_type_uses_runtime_type_var_identity() -> None:
    left = ta.TypeVar('T')  # type: ignore
    right = ta.TypeVar('T')  # type: ignore

    typ = reflect_substitute_type(
        dict[left, right],  # type: ignore
        {left: int},
        RuntimeTypeReflector(RuntimeTypeUniverse()),
    )

    assert type_str(typ) == 'builtins.dict[builtins.int, T]'
    assert isinstance(typ, types.Instance)
    assert isinstance(typ.args[1], types.TypeVarType)


def test_reflect_substitute_type_uses_identity_for_bounded_type_var() -> None:
    left = ta.TypeVar('T', bound=cabc.Sequence[int])  # type: ignore
    right = ta.TypeVar('T', bound=cabc.Sequence[int])  # type: ignore

    typ = reflect_substitute_type(
        tuple[left, right],  # type: ignore
        {left: str},
        RuntimeTypeReflector(RuntimeTypeUniverse()),
    )

    assert type_str(typ) == 'tuple[builtins.str, T]'
    assert isinstance(typ, types.TupleType)
    assert isinstance(typ.items[1], types.TypeVarType)


def test_reflect_substitute_type_uses_identity_for_constrained_type_var() -> None:
    left = ta.TypeVar('T', int, str)  # type: ignore
    right = ta.TypeVar('T', int, str)  # type: ignore

    typ = reflect_substitute_type(
        tuple[left, right],  # type: ignore
        {left: float},
        RuntimeTypeReflector(RuntimeTypeUniverse()),
    )

    assert type_str(typ) == 'tuple[builtins.float, T]'
    assert isinstance(typ, types.TupleType)
    assert isinstance(typ.items[1], types.TypeVarType)


def test_reflect_substitute_types_reuses_explicit_reflector_cache() -> None:
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    t_var = ta.TypeVar('T')  # type: ignore

    substituted = reflect_substitute_types([list[t_var]], {t_var: int}, reflector)  # type: ignore
    direct = reflect_substitute_type(list[t_var], {t_var: int}, reflector)  # type: ignore

    assert len(substituted) == 1
    assert type_str(substituted[0]) == type_str(direct)


def test_reflect_substitute_types_rejects_non_type_var_runtime_key() -> None:
    with pytest.raises(ReflectionError, match='substitution key'):
        reflect_substitute_types([list[int]], {int: str}, RuntimeTypeReflector(RuntimeTypeUniverse()))
