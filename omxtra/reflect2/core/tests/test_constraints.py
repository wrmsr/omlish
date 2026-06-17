# ruff: noqa: SLF001
import typing as ta

import pytest

from ...errors import UnsupportedTypeOperationError
from .. import symbols
from .. import types
from ..constraints import Constraint
from ..constraints import ConstraintOp
from ..constraints import infer_constraints
from ..join import join_types
from ..meet import meet_types
from ..solve import solve_constraints
from ..solve import solve_one
from ..strconv import type_str
from ..substitute import substitute_type
from ..subtypes import is_same_type
from ..subtypes import is_structurally_equivalent
from .helpers import make_any
from .helpers import make_info
from .helpers import make_instance
from .helpers import make_recursive_json_like_alias_case
from .helpers import make_recursive_mixed_tuple_alias_case
from .helpers import make_recursive_variadic_tuple_alias_case
from .helpers import make_type_var
from .helpers import make_type_var_tuple
from .helpers import make_typed_dict


def test_infer_direct_type_var_constraint() -> None:
    t_var = make_type_var('T', 1)
    int_type = make_instance(make_info('builtins.int'))

    constraints = infer_constraints(t_var, int_type, ConstraintOp.SUPERTYPE_OF)

    assert len(constraints) == 1
    assert constraints[0].origin_type_var is t_var
    assert constraints[0].type_var is t_var.id
    assert constraints[0].op == ConstraintOp.SUPERTYPE_OF
    assert constraints[0].target is int_type


def test_solve_direct_type_var_constraint() -> None:
    t_var = make_type_var('T', 1)
    int_type = make_instance(make_info('builtins.int'))

    constraints = infer_constraints(t_var, int_type, ConstraintOp.SUPERTYPE_OF)

    assert solve_constraints([t_var], constraints) == [int_type]


def test_infer_covariant_generic_instance_constraints() -> None:
    t_var = make_type_var('T', 1)
    int_type = make_instance(make_info('builtins.int'))
    box_info = symbols.TypeInfo('Box', 'Box', type_vars=[t_var], variances=[symbols.VarianceKind.CO])

    constraints = infer_constraints(
        make_instance(box_info, [t_var]),
        make_instance(box_info, [int_type]),
        ConstraintOp.SUPERTYPE_OF,
    )

    assert [constraint.op for constraint in constraints] == [ConstraintOp.SUPERTYPE_OF]
    assert is_same_type(constraints[0].target, int_type)
    assert solve_constraints([t_var], constraints) == [int_type]


def test_infer_contravariant_generic_instance_constraints() -> None:
    t_var = make_type_var('T', 1)
    int_type = make_instance(make_info('builtins.int'))
    sink_info = symbols.TypeInfo('Sink', 'Sink', type_vars=[t_var], variances=[symbols.VarianceKind.CONTRA])

    constraints = infer_constraints(
        make_instance(sink_info, [t_var]),
        make_instance(sink_info, [int_type]),
        ConstraintOp.SUPERTYPE_OF,
    )

    assert [(constraint.op, constraint.target) for constraint in constraints] == [(ConstraintOp.SUBTYPE_OF, int_type)]
    assert solve_constraints([t_var], constraints) == [int_type]


def test_infer_invariant_generic_instance_constraints() -> None:
    t_var = make_type_var('T', 1)
    int_type = make_instance(make_info('builtins.int'))
    box_info = symbols.TypeInfo('Box', 'Box', type_vars=[t_var], variances=[symbols.VarianceKind.IN])

    constraints = infer_constraints(
        make_instance(box_info, [t_var]),
        make_instance(box_info, [int_type]),
        ConstraintOp.SUPERTYPE_OF,
    )

    assert [(constraint.op, constraint.target) for constraint in constraints] == [
        (ConstraintOp.SUPERTYPE_OF, int_type),
        (ConstraintOp.SUBTYPE_OF, int_type),
    ]
    assert solve_constraints([t_var], constraints) == [int_type]


def test_infer_generic_base_instance_constraints() -> None:
    t_var = make_type_var('T', 1)
    int_type = make_instance(make_info('builtins.int'))
    box_info = symbols.TypeInfo('Box', 'Box', type_vars=[t_var], variances=[symbols.VarianceKind.CO])
    child_info = make_info('IntBox')
    child_info._bases = (make_instance(box_info, [int_type]),)
    child_info._mro = (child_info, box_info)

    constraints = infer_constraints(
        make_instance(box_info, [t_var]),
        make_instance(child_info),
        ConstraintOp.SUPERTYPE_OF,
    )

    assert [constraint.op for constraint in constraints] == [ConstraintOp.SUPERTYPE_OF]
    assert is_same_type(constraints[0].target, int_type)
    assert type_str(ta.cast(types.Type, solve_constraints([t_var], constraints)[0])) == 'builtins.int'


def test_infer_type_type_constraints() -> None:
    t_var = make_type_var('T', 1)
    int_type = make_instance(make_info('builtins.int'))

    constraints = infer_constraints(types.TypeType(t_var), types.TypeType(int_type), ConstraintOp.SUPERTYPE_OF)

    assert [(constraint.op, constraint.target) for constraint in constraints] == [(ConstraintOp.SUPERTYPE_OF, int_type)]
    assert solve_constraints([t_var], constraints) == [int_type]


def test_infer_direct_param_spec_constraint_to_parameters() -> None:
    param_spec = types.ParamSpecType('P', 'P', types.TypeVarId(1), make_any(), make_any())
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))
    parameters = types.Parameters(
        [int_type, str_type],
        [symbols.ArgKind.POS, symbols.ArgKind.NAMED_OPT],
        [None, 'name'],
    )

    constraints = infer_constraints(param_spec, parameters, ConstraintOp.SUPERTYPE_OF)

    assert [(constraint.op, constraint.target) for constraint in constraints] == [
        (ConstraintOp.SUPERTYPE_OF, parameters),
    ]
    assert solve_constraints([param_spec], constraints) == [parameters]


def test_infer_callable_param_spec_constraint_to_actual_parameter_shape() -> None:
    param_spec = types.ParamSpecType('P', 'P', types.TypeVarId(1), make_any(), make_any())
    same_param_spec = types.ParamSpecType('P', 'P', types.TypeVarId(1), make_any(), make_any())
    ret_var = make_type_var('R', 2)
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))
    bool_type = make_instance(make_info('builtins.bool'))
    fallback = make_instance(make_info('function'))
    template = types.CallableType(
        [param_spec, same_param_spec],
        [symbols.ArgKind.STAR, symbols.ArgKind.STAR2],
        [None, None],
        ret_var,
        fallback,
        variables=[param_spec],
    )
    actual = types.CallableType(
        [int_type, str_type],
        [symbols.ArgKind.POS, symbols.ArgKind.NAMED_OPT],
        [None, 'name'],
        bool_type,
        fallback,
    )

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)
    solution = solve_constraints([ret_var, param_spec], constraints)

    assert [constraint.op for constraint in constraints] == [ConstraintOp.SUPERTYPE_OF, ConstraintOp.SUBTYPE_OF]
    assert constraints[0].target is bool_type
    assert isinstance(constraints[1].target, types.Parameters)
    assert solution[0] is bool_type
    assert solution[1] is constraints[1].target


def test_infer_callable_param_spec_constraint_preserves_named_parameter_shape() -> None:
    param_spec = types.ParamSpecType('P', 'P', types.TypeVarId(1), make_any(), make_any())
    same_param_spec = types.ParamSpecType('P', 'P', types.TypeVarId(1), make_any(), make_any())
    ret_var = make_type_var('R', 2)
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))
    bool_type = make_instance(make_info('builtins.bool'))
    bytes_type = make_instance(make_info('builtins.bytes'))
    fallback = make_instance(make_info('function'))
    template = types.CallableType(
        [param_spec, same_param_spec],
        [symbols.ArgKind.STAR, symbols.ArgKind.STAR2],
        [None, None],
        ret_var,
        fallback,
        variables=[param_spec],
    )
    actual = types.CallableType(
        [int_type, str_type, bool_type, bytes_type],
        [
            symbols.ArgKind.POS,
            symbols.ArgKind.OPT,
            symbols.ArgKind.NAMED,
            symbols.ArgKind.NAMED_OPT,
        ],
        [None, None, 'flag', 'payload'],
        bool_type,
        fallback,
    )

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)
    solution = solve_constraints([ret_var, param_spec], constraints)

    assert solution[0] is bool_type
    assert isinstance(solution[1], types.Parameters)
    assert list(solution[1].arg_types) == [int_type, str_type, bool_type, bytes_type]
    assert list(solution[1].arg_kinds) == [
        symbols.ArgKind.POS,
        symbols.ArgKind.OPT,
        symbols.ArgKind.NAMED,
        symbols.ArgKind.NAMED_OPT,
    ]
    assert list(solution[1].arg_names) == [None, None, 'flag', 'payload']


def test_infer_callable_concatenate_param_spec_constraint_to_remaining_parameter_shape() -> None:
    param_spec = types.ParamSpecType('P', 'P', types.TypeVarId(1), make_any(), make_any())
    same_param_spec = types.ParamSpecType('P', 'P', types.TypeVarId(1), make_any(), make_any())
    prefix_var = make_type_var('T', 2)
    ret_var = make_type_var('R', 3)
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))
    bool_type = make_instance(make_info('builtins.bool'))
    fallback = make_instance(make_info('function'))
    template = types.CallableType(
        [prefix_var, param_spec, same_param_spec],
        [symbols.ArgKind.POS, symbols.ArgKind.STAR, symbols.ArgKind.STAR2],
        [None, None, None],
        ret_var,
        fallback,
        variables=[param_spec],
    )
    actual = types.CallableType(
        [int_type, str_type],
        [symbols.ArgKind.POS, symbols.ArgKind.POS],
        [None, None],
        bool_type,
        fallback,
    )

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)
    solution = solve_constraints([ret_var, prefix_var, param_spec], constraints)

    assert [constraint.op for constraint in constraints] == [
        ConstraintOp.SUPERTYPE_OF,
        ConstraintOp.SUBTYPE_OF,
        ConstraintOp.SUBTYPE_OF,
    ]
    assert solution[0] is bool_type
    assert solution[1] is int_type
    assert isinstance(solution[2], types.Parameters)
    assert [type_str(arg) for arg in solution[2].arg_types] == ['builtins.str']


def test_infer_callable_concatenate_preserves_remaining_named_parameter_shape() -> None:
    param_spec = types.ParamSpecType('P', 'P', types.TypeVarId(1), make_any(), make_any())
    same_param_spec = types.ParamSpecType('P', 'P', types.TypeVarId(1), make_any(), make_any())
    prefix_var = make_type_var('T', 2)
    ret_var = make_type_var('R', 3)
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))
    bool_type = make_instance(make_info('builtins.bool'))
    bytes_type = make_instance(make_info('builtins.bytes'))
    fallback = make_instance(make_info('function'))
    template = types.CallableType(
        [prefix_var, param_spec, same_param_spec],
        [symbols.ArgKind.POS, symbols.ArgKind.STAR, symbols.ArgKind.STAR2],
        [None, None, None],
        ret_var,
        fallback,
        variables=[param_spec],
    )
    actual = types.CallableType(
        [int_type, str_type, bool_type, bytes_type],
        [
            symbols.ArgKind.POS,
            symbols.ArgKind.OPT,
            symbols.ArgKind.NAMED,
            symbols.ArgKind.NAMED_OPT,
        ],
        [None, None, 'flag', 'payload'],
        bool_type,
        fallback,
    )

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)
    solution = solve_constraints([ret_var, prefix_var, param_spec], constraints)

    assert solution[0] is bool_type
    assert solution[1] is int_type
    assert isinstance(solution[2], types.Parameters)
    assert list(solution[2].arg_types) == [str_type, bool_type, bytes_type]
    assert list(solution[2].arg_kinds) == [
        symbols.ArgKind.OPT,
        symbols.ArgKind.NAMED,
        symbols.ArgKind.NAMED_OPT,
    ]
    assert list(solution[2].arg_names) == [None, 'flag', 'payload']


def test_infer_direct_type_var_tuple_constraint_to_tuple_type() -> None:
    tuple_info = make_info('builtins.tuple')
    tuple_fallback = make_instance(tuple_info, [make_any()])
    type_var_tuple = types.TypeVarTupleType('Ts', 'Ts', types.TypeVarId(1), make_any(), make_any(), tuple_fallback)
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))
    actual = types.TupleType([int_type, str_type], tuple_fallback)

    constraints = infer_constraints(type_var_tuple, actual, ConstraintOp.SUPERTYPE_OF)

    assert [(constraint.op, constraint.target) for constraint in constraints] == [
        (ConstraintOp.SUPERTYPE_OF, actual),
    ]
    assert solve_constraints([type_var_tuple], constraints) == [actual]


def test_infer_direct_type_var_tuple_constraint_to_type_list() -> None:
    tuple_fallback = make_instance(make_info('builtins.tuple'), [make_any()])
    type_var_tuple = types.TypeVarTupleType('Ts', 'Ts', types.TypeVarId(1), make_any(), make_any(), tuple_fallback)
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))
    actual = types.TypeList([int_type, str_type])

    constraints = infer_constraints(type_var_tuple, actual, ConstraintOp.SUPERTYPE_OF)

    assert [(constraint.op, constraint.target) for constraint in constraints] == [
        (ConstraintOp.SUPERTYPE_OF, actual),
    ]
    assert solve_constraints([type_var_tuple], constraints) == [actual]


def test_infer_constraints_expands_nonrecursive_template_alias() -> None:
    t_var = make_type_var('T', 1)
    int_type = make_instance(make_info('builtins.int'))
    box_info = symbols.TypeInfo('Box', 'Box', type_vars=[t_var], variances=[symbols.VarianceKind.CO])
    alias = symbols.TypeAlias('Alias', make_instance(box_info, [t_var]), alias_tvars=[t_var])

    constraints = infer_constraints(
        types.TypeAliasType(alias, [t_var]),
        make_instance(box_info, [int_type]),
        ConstraintOp.SUPERTYPE_OF,
    )

    assert [(constraint.op, constraint.target) for constraint in constraints] == [(ConstraintOp.SUPERTYPE_OF, int_type)]
    assert solve_constraints([t_var], constraints) == [int_type]


def test_infer_constraints_expands_nonrecursive_type_var_tuple_template_alias() -> None:
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))
    tuple_info = make_info('builtins.tuple')
    fallback = make_instance(tuple_info, [make_any()])
    type_var_tuple = types.TypeVarTupleType('Ts', 'Ts', types.TypeVarId(1), make_any(), make_any(), fallback)
    alias = symbols.TypeAlias(
        'Alias',
        types.TupleType([types.UnpackType(type_var_tuple)], fallback),
        alias_tvars=[type_var_tuple],
    )

    constraints = infer_constraints(
        types.TypeAliasType(alias, [type_var_tuple]),
        types.TupleType([int_type, str_type], fallback),
        ConstraintOp.SUPERTYPE_OF,
    )
    solution = solve_constraints([type_var_tuple], constraints)

    assert isinstance(solution[0], types.TupleType)
    assert list(solution[0].items) == [int_type, str_type]


def test_infer_constraints_expands_nonrecursive_actual_alias() -> None:
    t_var = make_type_var('T', 1)
    int_type = make_instance(make_info('builtins.int'))
    box_info = symbols.TypeInfo('Box', 'Box', type_vars=[t_var], variances=[symbols.VarianceKind.CO])
    alias = symbols.TypeAlias('Alias', make_instance(box_info, [int_type]))

    constraints = infer_constraints(
        make_instance(box_info, [t_var]),
        types.TypeAliasType(alias, []),
        ConstraintOp.SUPERTYPE_OF,
    )

    assert [(constraint.op, constraint.target) for constraint in constraints] == [(ConstraintOp.SUPERTYPE_OF, int_type)]
    assert solve_constraints([t_var], constraints) == [int_type]


def test_infer_constraints_expands_annotated_aliases_in_template_and_actual() -> None:
    t_var = make_type_var('T', 1)
    int_type = make_instance(make_info('builtins.int'))
    box_info = symbols.TypeInfo('Box', 'Box', type_vars=[t_var], variances=[symbols.VarianceKind.CO])
    template_alias = symbols.TypeAlias('TemplateAlias', make_instance(box_info, [t_var]), alias_tvars=[t_var])
    actual_alias = symbols.TypeAlias('ActualAlias', make_instance(box_info, [int_type]))

    constraints = infer_constraints(
        types.AnnotatedType(types.TypeAliasType(template_alias, [t_var]), ('template',)),
        types.AnnotatedType(types.TypeAliasType(actual_alias, []), ('actual',)),
        ConstraintOp.SUPERTYPE_OF,
    )

    assert [(constraint.op, constraint.target) for constraint in constraints] == [(ConstraintOp.SUPERTYPE_OF, int_type)]
    assert solve_constraints([t_var], constraints) == [int_type]


def test_infer_union_constraints_solves_optional_type_var() -> None:
    t_var = make_type_var('T', 1)
    int_type = make_instance(make_info('builtins.int'))

    constraints = infer_constraints(
        types.UnionType([t_var, types.NoneType()]),
        types.UnionType([int_type, types.NoneType()]),
        ConstraintOp.SUPERTYPE_OF,
    )

    assert [(constraint.op, constraint.target) for constraint in constraints] == [(ConstraintOp.SUPERTYPE_OF, int_type)]
    assert solve_constraints([t_var], constraints) == [int_type]


def test_infer_union_constraints_solves_optional_generic_instance() -> None:
    t_var = make_type_var('T', 1)
    int_type = make_instance(make_info('builtins.int'))
    list_info = symbols.TypeInfo(
        'builtins.list',
        'builtins.list',
        type_vars=[t_var],
        variances=[symbols.VarianceKind.IN],
    )

    constraints = infer_constraints(
        types.UnionType([make_instance(list_info, [t_var]), types.NoneType()]),
        types.UnionType([types.NoneType(), make_instance(list_info, [int_type])]),
        ConstraintOp.SUPERTYPE_OF,
    )

    assert [(constraint.op, constraint.target) for constraint in constraints] == [
        (ConstraintOp.SUPERTYPE_OF, int_type),
        (ConstraintOp.SUBTYPE_OF, int_type),
    ]
    assert solve_constraints([t_var], constraints) == [int_type]


def test_infer_union_constraints_expands_optional_alias() -> None:
    t_var = make_type_var('T', 1)
    int_type = make_instance(make_info('builtins.int'))
    alias = symbols.TypeAlias(
        'Maybe',
        types.UnionType([t_var, types.NoneType()]),
        alias_tvars=[t_var],
    )

    constraints = infer_constraints(
        types.TypeAliasType(alias, [t_var]),
        types.UnionType([int_type, types.NoneType()]),
        ConstraintOp.SUPERTYPE_OF,
    )

    assert [(constraint.op, constraint.target) for constraint in constraints] == [(ConstraintOp.SUPERTYPE_OF, int_type)]
    assert solve_constraints([t_var], constraints) == [int_type]


def test_infer_union_constraints_fail_closed_for_ambiguous_type_var_branches() -> None:
    t_var = make_type_var('T', 1)
    u_var = make_type_var('U', 2)
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))

    with pytest.raises(UnsupportedTypeOperationError, match='ambiguous Union'):
        infer_constraints(
            types.UnionType([t_var, u_var]),
            types.UnionType([int_type, str_type]),
            ConstraintOp.SUPERTYPE_OF,
        )


def test_infer_union_constraints_fail_closed_for_unmatched_concrete_branch() -> None:
    t_var = make_type_var('T', 1)
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))

    with pytest.raises(UnsupportedTypeOperationError, match='unmatched concrete item'):
        infer_constraints(
            types.UnionType([t_var, types.NoneType()]),
            types.UnionType([int_type, str_type]),
            ConstraintOp.SUPERTYPE_OF,
        )


def test_infer_union_constraints_fail_closed_for_ambiguous_structural_recursive_branches() -> None:
    list_info = make_info('builtins.list')
    box_info = make_info('Box')
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))
    alias = symbols.TypeAlias('Node', make_any())
    alias_type = types.TypeAliasType(alias, [])
    alias._target = types.UnionType([int_type, make_instance(list_info, [alias_type])])
    template = types.UnionType([make_instance(box_info, [alias_type]), str_type])
    actual = types.UnionType([
        make_instance(box_info, [alias.target]),
        make_instance(box_info, [alias_type]),
    ])

    with pytest.raises(UnsupportedTypeOperationError, match='unmatched concrete item'):
        infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)


def test_infer_tuple_constraints_solves_fixed_items_positionally() -> None:
    t_var = make_type_var('T', 1)
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))
    tuple_info = make_info('builtins.tuple')
    fallback = make_instance(tuple_info, [make_any()])

    constraints = infer_constraints(
        types.TupleType([t_var, str_type], fallback),
        types.TupleType([int_type, str_type], fallback),
        ConstraintOp.SUPERTYPE_OF,
    )

    assert [(constraint.op, constraint.target) for constraint in constraints] == [(ConstraintOp.SUPERTYPE_OF, int_type)]
    assert solve_constraints([t_var], constraints) == [int_type]


def test_infer_tuple_constraints_ignores_subtype_compatible_concrete_items() -> None:
    t_var = make_type_var('T', 1)
    object_info = make_info('builtins.object')
    str_info = make_info('builtins.str')
    str_info._mro = (str_info, object_info)
    int_type = make_instance(make_info('builtins.int'))
    object_type = make_instance(object_info)
    str_type = make_instance(str_info)
    fallback = make_instance(make_info('builtins.tuple'), [make_any()])

    constraints = infer_constraints(
        types.TupleType([t_var, object_type], fallback),
        types.TupleType([int_type, str_type], fallback),
        ConstraintOp.SUPERTYPE_OF,
    )

    assert [(constraint.op, constraint.target) for constraint in constraints] == [(ConstraintOp.SUPERTYPE_OF, int_type)]
    assert solve_constraints([t_var], constraints) == [int_type]


def test_infer_tuple_constraints_from_join_derived_fixed_tuple_shape() -> None:
    t_var = make_type_var('T', 1)
    object_info = make_info('builtins.object')
    int_info = make_info('builtins.int')
    str_info = make_info('builtins.str')
    int_info._mro = (int_info, object_info)
    str_info._mro = (str_info, object_info)
    object_type = make_instance(object_info)
    fallback = make_instance(make_info('builtins.tuple'), [make_any()])
    joined = join_types(
        types.TupleType([make_instance(int_info), object_type], fallback),
        types.TupleType([object_type, make_instance(str_info)], fallback),
    )

    assert isinstance(joined, types.TupleType)

    constraints = infer_constraints(
        types.TupleType([t_var, object_type], fallback),
        joined,
        ConstraintOp.SUPERTYPE_OF,
    )

    assert [(constraint.op, constraint.target) for constraint in constraints] == [
        (ConstraintOp.SUPERTYPE_OF, object_type),
    ]
    assert solve_constraints([t_var], constraints) == [object_type]


def test_infer_tuple_constraints_from_meet_derived_fixed_tuple_shape() -> None:
    t_var = make_type_var('T', 1)
    object_info = make_info('builtins.object')
    int_info = make_info('builtins.int')
    str_info = make_info('builtins.str')
    int_info._mro = (int_info, object_info)
    str_info._mro = (str_info, object_info)
    object_type = make_instance(object_info)
    int_type = make_instance(int_info)
    str_type = make_instance(str_info)
    fallback = make_instance(make_info('builtins.tuple'), [make_any()])
    met = meet_types(
        types.TupleType([int_type, object_type], fallback),
        types.TupleType([object_type, str_type], fallback),
    )

    assert isinstance(met, types.TupleType)

    constraints = infer_constraints(
        types.TupleType([t_var, str_type], fallback),
        met,
        ConstraintOp.SUPERTYPE_OF,
    )

    assert [(constraint.op, constraint.target) for constraint in constraints] == [(ConstraintOp.SUPERTYPE_OF, int_type)]
    assert solve_constraints([t_var], constraints) == [int_type]


def test_infer_tuple_constraints_respects_subtype_direction() -> None:
    t_var = make_type_var('T', 1)
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))
    tuple_info = make_info('builtins.tuple')
    fallback = make_instance(tuple_info, [make_any()])

    constraints = infer_constraints(
        types.TupleType([t_var, str_type], fallback),
        types.TupleType([int_type, str_type], fallback),
        ConstraintOp.SUBTYPE_OF,
    )

    assert [(constraint.op, constraint.target) for constraint in constraints] == [(ConstraintOp.SUBTYPE_OF, int_type)]
    assert solve_constraints([t_var], constraints) == [int_type]


def test_infer_tuple_constraints_composes_with_optional_alias() -> None:
    t_var = make_type_var('T', 1)
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))
    tuple_info = make_info('builtins.tuple')
    fallback = make_instance(tuple_info, [make_any()])
    alias = symbols.TypeAlias(
        'MaybePair',
        types.UnionType([types.TupleType([t_var, str_type], fallback), types.NoneType()]),
        alias_tvars=[t_var],
    )

    constraints = infer_constraints(
        types.TypeAliasType(alias, [t_var]),
        types.UnionType([types.NoneType(), types.TupleType([int_type, str_type], fallback)]),
        ConstraintOp.SUPERTYPE_OF,
    )

    assert [(constraint.op, constraint.target) for constraint in constraints] == [(ConstraintOp.SUPERTYPE_OF, int_type)]
    assert solve_constraints([t_var], constraints) == [int_type]


def test_infer_tuple_constraints_fail_closed_for_mismatched_length() -> None:
    t_var = make_type_var('T', 1)
    int_type = make_instance(make_info('builtins.int'))
    tuple_info = make_info('builtins.tuple')
    fallback = make_instance(tuple_info, [make_any()])

    with pytest.raises(UnsupportedTypeOperationError, match='mismatched items'):
        infer_constraints(
            types.TupleType([t_var], fallback),
            types.TupleType([int_type, int_type], fallback),
            ConstraintOp.SUPERTYPE_OF,
        )


def test_infer_tuple_constraints_fail_closed_for_mismatched_fallback() -> None:
    t_var = make_type_var('T', 1)
    int_type = make_instance(make_info('builtins.int'))

    with pytest.raises(UnsupportedTypeOperationError, match='mismatched fallbacks'):
        infer_constraints(
            types.TupleType([t_var], make_instance(make_info('builtins.tuple'), [make_any()])),
            types.TupleType([int_type], make_instance(make_info('other.tuple'), [make_any()])),
            ConstraintOp.SUPERTYPE_OF,
        )


def test_infer_tuple_constraints_solve_unpack_type_var_tuple_item() -> None:
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))
    tuple_info = make_info('builtins.tuple')
    fallback = make_instance(tuple_info, [make_any()])
    type_var_tuple = types.TypeVarTupleType('Ts', 'Ts', types.TypeVarId(1), make_any(), make_any(), fallback)

    constraints = infer_constraints(
        types.TupleType([types.UnpackType(type_var_tuple)], fallback),
        types.TupleType([int_type, str_type], fallback),
        ConstraintOp.SUPERTYPE_OF,
    )
    solution = solve_constraints([type_var_tuple], constraints)

    assert [constraint.op for constraint in constraints] == [ConstraintOp.SUPERTYPE_OF]
    assert isinstance(constraints[0].target, types.TupleType)
    assert list(constraints[0].target.items) == [int_type, str_type]
    assert isinstance(solution[0], types.TupleType)
    assert list(solution[0].items) == [int_type, str_type]


def test_infer_tuple_constraints_expands_variadic_alias_with_packed_arg() -> None:
    head_var = make_type_var('Head', 1)
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))
    bool_type = make_instance(make_info('builtins.bool'))
    fallback = make_instance(make_info('builtins.tuple'), [make_any()])
    type_var_tuple = make_type_var_tuple('Ts', 2)
    alias = symbols.TypeAlias(
        'Alias',
        types.TupleType([head_var, types.UnpackType(type_var_tuple)], fallback),
        alias_tvars=[head_var, type_var_tuple],
    )

    constraints = infer_constraints(
        types.TypeAliasType(alias, [head_var, types.TupleType([str_type, bool_type], fallback)]),
        types.TupleType([int_type, str_type, bool_type], fallback),
        ConstraintOp.SUPERTYPE_OF,
    )

    assert [(constraint.op, constraint.target) for constraint in constraints] == [(ConstraintOp.SUPERTYPE_OF, int_type)]
    assert solve_constraints([head_var], constraints) == [int_type]


def test_infer_tuple_constraints_expands_variadic_actual_alias_with_packed_arg() -> None:
    type_var_tuple = make_type_var_tuple('Ts', 1)
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))
    fallback = make_instance(make_info('builtins.tuple'), [make_any()])
    alias = symbols.TypeAlias(
        'Alias',
        types.TupleType([types.UnpackType(type_var_tuple)], fallback),
        alias_tvars=[type_var_tuple],
    )

    constraints = infer_constraints(
        types.TupleType([types.UnpackType(type_var_tuple)], fallback),
        types.TypeAliasType(alias, [types.TupleType([int_type, str_type], fallback)]),
        ConstraintOp.SUPERTYPE_OF,
    )
    solution = solve_constraints([type_var_tuple], constraints)

    assert isinstance(solution[0], types.TupleType)
    assert list(solution[0].items) == [int_type, str_type]


def test_infer_tuple_constraints_unrolls_recursive_variadic_alias_template() -> None:
    case = make_recursive_variadic_tuple_alias_case('TupleNode', 1)

    constraints = infer_constraints(case.alias_type, case.one_unrolling, ConstraintOp.SUPERTYPE_OF)
    solution = solve_constraints([case.type_var_tuple], constraints)

    assert all(constraint.op is ConstraintOp.SUPERTYPE_OF for constraint in constraints)
    assert isinstance(solution[0], types.TupleType)
    assert list(solution[0].items) == case.concrete_items


def test_infer_tuple_constraints_unrolls_recursive_variadic_alias_actual() -> None:
    case = make_recursive_variadic_tuple_alias_case('TupleNode', 1)

    constraints = infer_constraints(case.one_unrolling, case.concrete_alias_type, ConstraintOp.SUPERTYPE_OF)

    assert constraints == []


def test_infer_tuple_constraints_solve_bare_type_var_tuple_item() -> None:
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))
    tuple_info = make_info('builtins.tuple')
    fallback = make_instance(tuple_info, [make_any()])
    type_var_tuple = types.TypeVarTupleType('Ts', 'Ts', types.TypeVarId(1), make_any(), make_any(), fallback)

    constraints = infer_constraints(
        types.TupleType([type_var_tuple], fallback),
        types.TupleType([int_type, str_type], fallback),
        ConstraintOp.SUPERTYPE_OF,
    )
    solution = solve_constraints([type_var_tuple], constraints)

    assert isinstance(solution[0], types.TupleType)
    assert list(solution[0].items) == [int_type, str_type]


def test_infer_tuple_constraints_solve_type_var_tuple_between_prefix_and_suffix() -> None:
    head_var = make_type_var('Head', 1)
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))
    bool_type = make_instance(make_info('builtins.bool'))
    bytes_type = make_instance(make_info('builtins.bytes'))
    tuple_info = make_info('builtins.tuple')
    fallback = make_instance(tuple_info, [make_any()])
    type_var_tuple = types.TypeVarTupleType('Ts', 'Ts', types.TypeVarId(2), make_any(), make_any(), fallback)

    constraints = infer_constraints(
        types.TupleType([head_var, types.UnpackType(type_var_tuple), bytes_type], fallback),
        types.TupleType([int_type, str_type, bool_type, bytes_type], fallback),
        ConstraintOp.SUPERTYPE_OF,
    )
    solution = solve_constraints([head_var, type_var_tuple], constraints)

    assert solution[0] is int_type
    assert isinstance(solution[1], types.TupleType)
    assert list(solution[1].items) == [str_type, bool_type]


def test_infer_tuple_constraints_solve_empty_type_var_tuple_slice() -> None:
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))
    tuple_info = make_info('builtins.tuple')
    fallback = make_instance(tuple_info, [make_any()])
    type_var_tuple = types.TypeVarTupleType('Ts', 'Ts', types.TypeVarId(1), make_any(), make_any(), fallback)

    constraints = infer_constraints(
        types.TupleType([int_type, types.UnpackType(type_var_tuple), str_type], fallback),
        types.TupleType([int_type, str_type], fallback),
        ConstraintOp.SUPERTYPE_OF,
    )
    solution = solve_constraints([type_var_tuple], constraints)

    assert isinstance(solution[0], types.TupleType)
    assert list(solution[0].items) == []


def test_infer_tuple_constraints_fail_closed_for_non_type_var_tuple_unpack_item() -> None:
    t_var = make_type_var('T', 1)
    int_type = make_instance(make_info('builtins.int'))
    tuple_info = make_info('builtins.tuple')
    fallback = make_instance(tuple_info, [make_any()])

    with pytest.raises(UnsupportedTypeOperationError, match='variadic Tuple'):
        infer_constraints(
            types.TupleType([types.UnpackType(t_var)], fallback),
            types.TupleType([int_type], fallback),
            ConstraintOp.SUPERTYPE_OF,
        )


def test_infer_tuple_constraints_fail_closed_for_multiple_type_var_tuple_items() -> None:
    int_type = make_instance(make_info('builtins.int'))
    tuple_info = make_info('builtins.tuple')
    fallback = make_instance(tuple_info, [make_any()])
    left_type_var_tuple = types.TypeVarTupleType('Ts', 'Ts', types.TypeVarId(1), make_any(), make_any(), fallback)
    right_type_var_tuple = types.TypeVarTupleType('Us', 'Us', types.TypeVarId(2), make_any(), make_any(), fallback)

    with pytest.raises(UnsupportedTypeOperationError, match='variadic Tuple'):
        infer_constraints(
            types.TupleType([types.UnpackType(left_type_var_tuple), types.UnpackType(right_type_var_tuple)], fallback),
            types.TupleType([int_type], fallback),
            ConstraintOp.SUPERTYPE_OF,
        )


def test_infer_tuple_constraints_fail_closed_for_variadic_actual_tuple() -> None:
    int_type = make_instance(make_info('builtins.int'))
    tuple_info = make_info('builtins.tuple')
    fallback = make_instance(tuple_info, [make_any()])
    type_var_tuple = types.TypeVarTupleType('Ts', 'Ts', types.TypeVarId(1), make_any(), make_any(), fallback)

    with pytest.raises(UnsupportedTypeOperationError, match='variadic Tuple'):
        infer_constraints(
            types.TupleType([int_type], fallback),
            types.TupleType([types.UnpackType(type_var_tuple)], fallback),
            ConstraintOp.SUPERTYPE_OF,
        )


def test_infer_typed_dict_constraints_uses_mutable_item_invariance() -> None:
    t_var = make_type_var('T', 1)
    int_type = make_instance(make_info('builtins.int'))
    fallback = make_instance(make_info('builtins.dict'))
    template = types.TypedDictType({'value': t_var}, {'value'}, set(), fallback)
    actual = types.TypedDictType({'value': int_type}, {'value'}, set(), fallback)

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)

    assert [(constraint.op, constraint.target) for constraint in constraints] == [
        (ConstraintOp.SUPERTYPE_OF, int_type),
        (ConstraintOp.SUBTYPE_OF, int_type),
    ]
    assert solve_constraints([t_var], constraints) == [int_type]


def test_infer_typed_dict_constraints_uses_readonly_item_covariance() -> None:
    t_var = make_type_var('T', 1)
    int_type = make_instance(make_info('builtins.int'))
    fallback = make_instance(make_info('builtins.dict'))
    template = types.TypedDictType({'value': t_var}, {'value'}, {'value'}, fallback)
    actual = types.TypedDictType({'value': int_type}, {'value'}, {'value'}, fallback)

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)

    assert [(constraint.op, constraint.target) for constraint in constraints] == [(ConstraintOp.SUPERTYPE_OF, int_type)]
    assert solve_constraints([t_var], constraints) == [int_type]


def test_infer_typed_dict_constraints_fails_closed_for_mismatched_keys() -> None:
    t_var = make_type_var('T', 1)
    int_type = make_instance(make_info('builtins.int'))
    template = make_typed_dict({'value': t_var}, {'value'})
    actual = make_typed_dict({'other': int_type}, {'other'})

    with pytest.raises(UnsupportedTypeOperationError, match='mismatched keys'):
        infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)


def test_infer_typed_dict_constraints_fails_closed_for_mismatched_required_keys() -> None:
    t_var = make_type_var('T', 1)
    int_type = make_instance(make_info('builtins.int'))
    template = make_typed_dict({'value': t_var}, {'value'})
    actual = make_typed_dict({'value': int_type}, set())

    with pytest.raises(UnsupportedTypeOperationError, match='mismatched required keys'):
        infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)


def test_infer_typed_dict_constraints_fails_closed_for_mismatched_readonly_keys() -> None:
    t_var = make_type_var('T', 1)
    int_type = make_instance(make_info('builtins.int'))
    template = make_typed_dict({'value': t_var}, {'value'}, {'value'})
    actual = make_typed_dict({'value': int_type}, {'value'})

    with pytest.raises(UnsupportedTypeOperationError, match='mismatched readonly keys'):
        infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)


def test_infer_typed_dict_constraints_fails_closed_for_mismatched_fallbacks() -> None:
    t_var = make_type_var('T', 1)
    int_type = make_instance(make_info('builtins.int'))
    template = make_typed_dict({'value': t_var}, {'value'})
    actual = types.TypedDictType(
        {'value': int_type},
        {'value'},
        set(),
        make_instance(make_info('collections.abc.Mapping')),
    )

    with pytest.raises(UnsupportedTypeOperationError, match='mismatched fallbacks'):
        infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)


def test_infer_typed_dict_constraints_propagates_item_failures() -> None:
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))
    fallback = make_instance(make_info('builtins.dict'))
    template = types.TypedDictType({'value': int_type}, {'value'}, set(), fallback)
    actual = types.TypedDictType({'value': str_type}, {'value'}, set(), fallback)

    with pytest.raises(UnsupportedTypeOperationError, match='instance constraint inference'):
        infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)


def test_infer_callable_constraints_uses_argument_contravariance() -> None:
    t_var = make_type_var('T', 1)
    int_type = make_instance(make_info('builtins.int'))
    fallback = make_instance(make_info('function'))
    template = types.CallableType([t_var], [symbols.ArgKind.POS], [None], t_var, fallback)
    actual = types.CallableType([int_type], [symbols.ArgKind.POS], [None], int_type, fallback)

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)

    assert [(constraint.op, constraint.target) for constraint in constraints] == [
        (ConstraintOp.SUPERTYPE_OF, int_type),
        (ConstraintOp.SUBTYPE_OF, int_type),
    ]
    assert solve_constraints([t_var], constraints) == [int_type]


def test_infer_callable_constraints_reverses_argument_direction_for_subtype_constraints() -> None:
    t_var = make_type_var('T', 1)
    int_type = make_instance(make_info('builtins.int'))
    fallback = make_instance(make_info('function'))
    template = types.CallableType([t_var], [symbols.ArgKind.POS], [None], t_var, fallback)
    actual = types.CallableType([int_type], [symbols.ArgKind.POS], [None], int_type, fallback)

    constraints = infer_constraints(template, actual, ConstraintOp.SUBTYPE_OF)

    assert [(constraint.op, constraint.target) for constraint in constraints] == [
        (ConstraintOp.SUBTYPE_OF, int_type),
        (ConstraintOp.SUPERTYPE_OF, int_type),
    ]
    assert solve_constraints([t_var], constraints) == [int_type]


def test_infer_callable_constraints_supports_keyword_only_same_shape() -> None:
    t_var = make_type_var('T', 1)
    str_type = make_instance(make_info('builtins.str'))
    bool_type = make_instance(make_info('builtins.bool'))
    fallback = make_instance(make_info('function'))
    template = types.CallableType(
        [t_var],
        [symbols.ArgKind.NAMED_OPT],
        ['value'],
        bool_type,
        fallback,
    )
    actual = types.CallableType(
        [str_type],
        [symbols.ArgKind.NAMED_OPT],
        ['value'],
        bool_type,
        fallback,
    )

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)

    assert [(constraint.op, constraint.target) for constraint in constraints] == [(ConstraintOp.SUBTYPE_OF, str_type)]
    assert solve_constraints([t_var], constraints) == [str_type]


def test_solve_one_uses_joined_lowers_and_met_uppers() -> None:
    object_info = make_info('builtins.object')
    int_info = make_info('builtins.int')
    str_info = make_info('builtins.str')
    int_info._mro = (int_info, object_info)
    str_info._mro = (str_info, object_info)
    object_type = make_instance(object_info)
    int_type = make_instance(int_info)
    str_type = make_instance(str_info)

    assert type_str(ta.cast(types.Type, solve_one([int_type, str_type], [object_type]))) == (
        'Union[builtins.int, builtins.str]'
    )
    assert solve_one([object_type], [int_type]) is None


def test_solve_constraints_uses_structural_lattice_for_recursive_alias_bounds() -> None:
    list_info = make_info('builtins.list')
    tuple_fallback = make_instance(make_info('builtins.tuple'))
    int_type = make_instance(make_info('builtins.int'))
    t_var = make_type_var('T', 1)
    alias = symbols.TypeAlias('Node', make_any())
    alias_type = types.TypeAliasType(alias, [])
    alias._target = types.UnionType([int_type, make_instance(list_info, [alias_type])])
    one_unrolling = types.UnionType([int_type, make_instance(list_info, [alias.target])])
    template = types.TupleType([t_var, t_var], tuple_fallback)
    actual = types.TupleType([alias_type, one_unrolling], tuple_fallback)

    lower_constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)
    lower_solution = solve_constraints([t_var], lower_constraints)
    upper_solution = solve_constraints(
        [t_var],
        [
            Constraint(t_var, ConstraintOp.SUBTYPE_OF, alias_type),
            Constraint(t_var, ConstraintOp.SUBTYPE_OF, one_unrolling),
        ],
    )

    assert lower_solution[0] is not None
    assert upper_solution[0] is not None
    assert is_structurally_equivalent(lower_solution[0], alias_type)
    assert is_structurally_equivalent(upper_solution[0], alias_type)


def test_solve_constraints_uses_strict_default_for_unconstrained_vars() -> None:
    t_var = make_type_var('T', 1)

    strict_solution = solve_constraints([t_var], [])
    loose_solution = solve_constraints([t_var], [], strict=False)

    assert isinstance(strict_solution[0], types.UninhabitedType)
    assert isinstance(loose_solution[0], types.AnyType)
    assert loose_solution[0].type_of_any == types.TypeOfAny.SPECIAL_FORM


def test_solve_constraints_validates_upper_bound() -> None:
    object_info = make_info('builtins.object')
    int_info = make_info('builtins.int')
    int_info._mro = (int_info, object_info)
    int_type = make_instance(int_info)
    str_type = make_instance(make_info('builtins.str'))
    any_type = make_any()
    t_var = types.TypeVarType('T', 'T', types.TypeVarId(1), [], int_type, any_type)

    constraints = infer_constraints(t_var, str_type, ConstraintOp.SUPERTYPE_OF)

    assert solve_constraints([t_var], constraints) == [None]


def test_solve_constraints_validates_param_spec_solution_shape() -> None:
    param_spec = types.ParamSpecType('P', 'P', types.TypeVarId(1), make_any(), make_any())
    valid = types.Parameters(
        [make_instance(make_info('builtins.int'))],
        [symbols.ArgKind.POS],
        [None],
    )
    same_valid = types.Parameters(
        list(valid.arg_types),
        list(valid.arg_kinds),
        list(valid.arg_names),
    )
    different = types.Parameters(
        [make_instance(make_info('builtins.str'))],
        [symbols.ArgKind.POS],
        [None],
    )
    invalid = make_instance(make_info('builtins.int'))

    assert solve_constraints([param_spec], [Constraint(param_spec, ConstraintOp.SUPERTYPE_OF, valid)]) == [valid]
    assert solve_constraints(
        [param_spec],
        [
            Constraint(param_spec, ConstraintOp.SUPERTYPE_OF, valid),
            Constraint(param_spec, ConstraintOp.SUBTYPE_OF, same_valid),
        ],
    ) == [valid]
    assert solve_constraints(
        [param_spec],
        [
            Constraint(param_spec, ConstraintOp.SUPERTYPE_OF, valid),
            Constraint(param_spec, ConstraintOp.SUPERTYPE_OF, different),
        ],
    ) == [None]
    assert solve_constraints([param_spec], [Constraint(param_spec, ConstraintOp.SUPERTYPE_OF, invalid)]) == [None]


def test_solve_constraints_validates_type_var_tuple_solution_shape() -> None:
    tuple_fallback = make_instance(make_info('builtins.tuple'), [make_any()])
    type_var_tuple = types.TypeVarTupleType('Ts', 'Ts', types.TypeVarId(1), make_any(), make_any(), tuple_fallback)
    valid_tuple = types.TupleType([make_instance(make_info('builtins.int'))], tuple_fallback)
    same_valid_tuple = types.TupleType(list(valid_tuple.items), valid_tuple.partial_fallback)
    different_tuple = types.TupleType([make_instance(make_info('builtins.str'))], tuple_fallback)
    valid_list = types.TypeList([make_instance(make_info('builtins.str'))])
    invalid = make_instance(make_info('builtins.int'))

    assert solve_constraints(
        [type_var_tuple],
        [Constraint(type_var_tuple, ConstraintOp.SUPERTYPE_OF, valid_tuple)],
    ) == [valid_tuple]
    assert solve_constraints(
        [type_var_tuple],
        [
            Constraint(type_var_tuple, ConstraintOp.SUPERTYPE_OF, valid_tuple),
            Constraint(type_var_tuple, ConstraintOp.SUBTYPE_OF, same_valid_tuple),
        ],
    ) == [valid_tuple]
    assert solve_constraints(
        [type_var_tuple],
        [
            Constraint(type_var_tuple, ConstraintOp.SUPERTYPE_OF, valid_tuple),
            Constraint(type_var_tuple, ConstraintOp.SUPERTYPE_OF, different_tuple),
        ],
    ) == [None]
    assert solve_constraints(
        [type_var_tuple],
        [Constraint(type_var_tuple, ConstraintOp.SUPERTYPE_OF, valid_list)],
    ) == [valid_list]
    assert solve_constraints(
        [type_var_tuple],
        [Constraint(type_var_tuple, ConstraintOp.SUPERTYPE_OF, invalid)],
    ) == [None]


def test_infer_constraints_unrolls_recursive_alias_template() -> None:
    alias = symbols.TypeAlias('Alias', make_any())
    alias._target = types.UnionType([types.NoneType(), types.TypeAliasType(alias, [])])

    constraints = infer_constraints(
        types.TypeAliasType(alias, []),
        types.UnionType([types.NoneType(), types.TypeAliasType(alias, [])]),
        ConstraintOp.SUPERTYPE_OF,
    )

    assert constraints == []


def test_infer_constraints_unrolls_json_like_recursive_alias_template_and_actual() -> None:
    case = make_recursive_json_like_alias_case('Jsonish')

    assert infer_constraints(case.alias_type, case.one_unrolling, ConstraintOp.SUPERTYPE_OF) == []
    assert infer_constraints(case.one_unrolling, case.alias_type, ConstraintOp.SUPERTYPE_OF) == []


def test_infer_constraints_unrolls_recursive_alias_with_literal_and_newtype_leaves() -> None:
    list_info = make_info('builtins.list')
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))
    user_info = symbols.TypeInfo('UserId', 'example.UserId', new_type_supertype=int_type)
    user_id = make_instance(user_info)
    alias = symbols.TypeAlias('TaggedNode', make_any())
    alias_type = types.TypeAliasType(alias, [])
    alias._target = types.UnionType([
        types.LiteralType('user', str_type),
        user_id,
        make_instance(list_info, [alias_type]),
    ])
    one_unrolling = types.UnionType([
        types.LiteralType('user', str_type),
        user_id,
        make_instance(list_info, [alias.target]),
    ])

    assert infer_constraints(alias_type, one_unrolling, ConstraintOp.SUPERTYPE_OF) == []
    assert infer_constraints(one_unrolling, alias_type, ConstraintOp.SUPERTYPE_OF) == []


def test_infer_constraints_solves_repeated_recursive_alias_type_var_positions() -> None:
    tuple_fallback = make_instance(make_info('builtins.tuple'))
    t_var = make_type_var('T', 1)
    int_type = make_instance(make_info('builtins.int'))
    alias = symbols.TypeAlias('PairNode', make_any(), alias_tvars=[t_var])
    template = types.TypeAliasType(alias, [t_var])
    actual = types.TypeAliasType(alias, [int_type])
    alias._target = types.TupleType([t_var, t_var, template], tuple_fallback)
    one_unrolling = types.TupleType([int_type, int_type, actual], tuple_fallback)

    constraints = infer_constraints(template, one_unrolling, ConstraintOp.SUPERTYPE_OF)
    solution = solve_constraints([t_var], constraints)

    assert constraints
    assert all(constraint.target is int_type for constraint in constraints)
    assert solution == [int_type]
    assert is_structurally_equivalent(substitute_type(template, {t_var: solution[0]}), one_unrolling)


def test_infer_constraints_solves_recursive_mixed_type_var_and_type_var_tuple_alias() -> None:
    case = make_recursive_mixed_tuple_alias_case('MixedNode', 1, 2)

    constraints = infer_constraints(case.alias_type, case.one_unrolling, ConstraintOp.SUPERTYPE_OF)
    solution = solve_constraints([case.type_var, case.type_var_tuple], constraints)

    assert constraints
    assert solution[0] is case.concrete_type_var_item
    assert solution[1] is not None
    assert is_same_type(solution[1], case.packed_concrete_arg)
    substituted = substitute_type(
        case.alias_type,
        {
            case.type_var: solution[0],
            case.type_var_tuple: solution[1],
        },
    )
    assert is_structurally_equivalent(substituted, case.one_unrolling)


def test_infer_constraints_allows_type_var_to_capture_recursive_alias_actual() -> None:
    t_var = make_type_var('T', 1)
    alias = symbols.TypeAlias('Alias', make_any())
    alias_type = types.TypeAliasType(alias, [])
    alias._target = types.UnionType([types.NoneType(), types.TypeAliasType(alias, [])])

    constraints = infer_constraints(t_var, alias_type, ConstraintOp.SUPERTYPE_OF)

    assert [(constraint.op, constraint.target) for constraint in constraints] == [
        (ConstraintOp.SUPERTYPE_OF, alias_type),
    ]
    assert solve_constraints([t_var], constraints) == [alias_type]


def test_infer_constraints_fails_closed_for_generic_callable_shape() -> None:
    t_var = make_type_var('T', 1)
    int_type = make_instance(make_info('builtins.int'))
    fallback = make_instance(make_info('function'))
    template = types.CallableType([t_var], [symbols.ArgKind.POS], [None], int_type, fallback, variables=[t_var])

    with pytest.raises(UnsupportedTypeOperationError, match='generic Callable'):
        infer_constraints(template, template, ConstraintOp.SUPERTYPE_OF)


def test_infer_constraints_fails_closed_for_callable_ellipsis_shape() -> None:
    int_type = make_instance(make_info('builtins.int'))
    fallback = make_instance(make_info('function'))
    template = types.CallableType([], [], [], int_type, fallback, is_ellipsis_args=True)

    with pytest.raises(UnsupportedTypeOperationError, match='ellipsis Callable'):
        infer_constraints(template, template, ConstraintOp.SUPERTYPE_OF)


def test_infer_constraints_fails_closed_for_direct_param_spec_against_instance() -> None:
    param_spec = types.ParamSpecType('P', 'P', types.TypeVarId(1), make_any(), make_any())

    with pytest.raises(UnsupportedTypeOperationError, match='ParamSpec'):
        infer_constraints(param_spec, make_instance(make_info('builtins.int')), ConstraintOp.SUPERTYPE_OF)


def test_infer_constraints_fails_closed_for_direct_type_var_tuple_against_instance() -> None:
    fallback = make_instance(make_info('builtins.tuple'), [make_any()])
    type_var_tuple = types.TypeVarTupleType('Ts', 'Ts', types.TypeVarId(1), make_any(), make_any(), fallback)

    with pytest.raises(UnsupportedTypeOperationError, match='TypeVarTuple'):
        infer_constraints(type_var_tuple, make_instance(make_info('builtins.int')), ConstraintOp.SUPERTYPE_OF)


def test_infer_constraints_fails_closed_for_mismatched_callable_shape() -> None:
    t_var = make_type_var('T', 1)
    int_type = make_instance(make_info('builtins.int'))
    fallback = make_instance(make_info('function'))
    template = types.CallableType([t_var], [symbols.ArgKind.POS], [None], int_type, fallback)
    actual = types.CallableType([int_type], [symbols.ArgKind.NAMED], ['value'], int_type, fallback)

    with pytest.raises(UnsupportedTypeOperationError, match='mismatched args'):
        infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)


def test_infer_constraints_fails_closed_for_concatenate_prefix_name_mismatch() -> None:
    param_spec = types.ParamSpecType('P', 'P', types.TypeVarId(1), make_any(), make_any())
    same_param_spec = types.ParamSpecType('P', 'P', types.TypeVarId(1), make_any(), make_any())
    int_type = make_instance(make_info('builtins.int'))
    bool_type = make_instance(make_info('builtins.bool'))
    fallback = make_instance(make_info('function'))
    template = types.CallableType(
        [int_type, param_spec, same_param_spec],
        [symbols.ArgKind.NAMED, symbols.ArgKind.STAR, symbols.ArgKind.STAR2],
        ['expected', None, None],
        bool_type,
        fallback,
        variables=[param_spec],
    )
    actual = types.CallableType(
        [int_type],
        [symbols.ArgKind.NAMED],
        ['actual'],
        bool_type,
        fallback,
    )

    with pytest.raises(UnsupportedTypeOperationError, match='mismatched args'):
        infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)
