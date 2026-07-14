# ruff: noqa: SLF001
import pytest

from ...errors import UnsupportedTypeOperationError
from ..constraints import ConstraintOp
from ..constraints import infer_constraints
from ..solve import solve_constraints
from ..symbols import ArgKind
from ..types import CallableType
from ..types import Instance
from ..types import Overloaded
from ..types import Parameters
from ..types import ParamSpecType
from ..types import Type
from ..types import TypeVarId
from ..types import UninhabitedType
from .helpers import make_any
from .helpers import make_info
from .helpers import make_instance
from .helpers import make_type_var


def _callable(arg: Instance, ret: Instance, fallback: Instance) -> CallableType:
    return CallableType([arg], [ArgKind.POS], [None], ret, fallback)


def _param_spec_callable(param_spec: ParamSpecType, ret: Type, fallback: Instance) -> CallableType:
    return CallableType(
        [param_spec, param_spec],
        [ArgKind.STAR, ArgKind.STAR2],
        [None, None],
        ret,
        fallback,
        variables=[param_spec],
    )


def _concatenate_callable(prefix: Type, param_spec: ParamSpecType, ret: Type, fallback: Instance) -> CallableType:
    return CallableType(
        [prefix, param_spec, param_spec],
        [ArgKind.POS, ArgKind.STAR, ArgKind.STAR2],
        [None, None, None],
        ret,
        fallback,
        variables=[param_spec],
    )


def test_infer_overloaded_constraints_selects_single_matching_item() -> None:
    t_var = make_type_var('T', 1)
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))
    bool_type = make_instance(make_info('builtins.bool'))
    fallback = make_instance(make_info('function'))
    template = Overloaded([
        CallableType([int_type], [ArgKind.POS], [None], t_var, fallback),
        CallableType([str_type], [ArgKind.POS], [None], t_var, fallback),
    ])
    actual = _callable(int_type, bool_type, fallback)

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)

    assert [(constraint.op, constraint.target) for constraint in constraints] == \
           [(ConstraintOp.SUPERTYPE_OF, bool_type)]
    assert solve_constraints([t_var], constraints) == [bool_type]


def test_infer_overloaded_constraints_uses_callable_argument_contravariance() -> None:
    t_var = make_type_var('T', 1)
    int_type = make_instance(make_info('builtins.int'))
    bool_type = make_instance(make_info('builtins.bool'))
    fallback = make_instance(make_info('function'))
    template = Overloaded([
        CallableType([t_var], [ArgKind.POS], [None], bool_type, fallback),
    ])
    actual = _callable(int_type, bool_type, fallback)

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)

    assert [(constraint.op, constraint.target) for constraint in constraints] == [(ConstraintOp.SUBTYPE_OF, int_type)]
    assert solve_constraints([t_var], constraints) == [int_type]


def test_infer_overloaded_constraints_fails_closed_for_no_matching_item() -> None:
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))
    bool_type = make_instance(make_info('builtins.bool'))
    fallback = make_instance(make_info('function'))
    template = Overloaded([
        _callable(str_type, bool_type, fallback),
    ])
    actual = _callable(int_type, bool_type, fallback)

    with pytest.raises(UnsupportedTypeOperationError, match='0 matches'):
        infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)


def test_infer_overloaded_constraints_fails_closed_for_ambiguous_items() -> None:
    t_var = make_type_var('T', 1)
    int_type = make_instance(make_info('builtins.int'))
    bool_type = make_instance(make_info('builtins.bool'))
    fallback = make_instance(make_info('function'))
    template = Overloaded([
        CallableType([int_type], [ArgKind.POS], [None], t_var, fallback),
        CallableType([int_type], [ArgKind.POS], [None], t_var, fallback),
    ])
    actual = _callable(int_type, bool_type, fallback)

    with pytest.raises(UnsupportedTypeOperationError, match='2 matches'):
        infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)


def test_infer_overloaded_constraints_selects_param_spec_item() -> None:
    param_spec = ParamSpecType('P', 'P', TypeVarId(1), make_any(), make_any())
    ret_var = make_type_var('R', 2)
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))
    bool_type = make_instance(make_info('builtins.bool'))
    fallback = make_instance(make_info('function'))
    template = Overloaded([
        CallableType([str_type], [ArgKind.POS], [None], ret_var, fallback),
        _param_spec_callable(param_spec, ret_var, fallback),
    ])
    actual = CallableType(
        [int_type, str_type],
        [ArgKind.POS, ArgKind.POS],
        [None, None],
        bool_type,
        fallback,
    )

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)
    solution = solve_constraints([ret_var, param_spec], constraints)

    assert [constraint.op for constraint in constraints] == [ConstraintOp.SUPERTYPE_OF, ConstraintOp.SUBTYPE_OF]
    assert solution[0] is bool_type
    assert isinstance(solution[1], Parameters)
    assert list(solution[1].arg_types) == [int_type, str_type]
    assert list(solution[1].arg_kinds) == [ArgKind.POS, ArgKind.POS]
    assert list(solution[1].arg_names) == [None, None]


def test_infer_overloaded_constraints_selects_concatenate_item() -> None:
    param_spec = ParamSpecType('P', 'P', TypeVarId(1), make_any(), make_any())
    ret_var = make_type_var('R', 2)
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))
    bool_type = make_instance(make_info('builtins.bool'))
    fallback = make_instance(make_info('function'))
    template = Overloaded([
        _concatenate_callable(str_type, param_spec, ret_var, fallback),
        _concatenate_callable(int_type, param_spec, ret_var, fallback),
    ])
    actual = CallableType(
        [int_type, str_type],
        [ArgKind.POS, ArgKind.POS],
        [None, None],
        bool_type,
        fallback,
    )

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)
    solution = solve_constraints([ret_var, param_spec], constraints)

    assert [constraint.op for constraint in constraints] == [
        ConstraintOp.SUPERTYPE_OF,
        ConstraintOp.SUBTYPE_OF,
    ]
    assert solution[0] is bool_type
    assert isinstance(solution[1], Parameters)
    assert list(solution[1].arg_types) == [str_type]
    assert list(solution[1].arg_kinds) == [ArgKind.POS]
    assert list(solution[1].arg_names) == [None]


def test_infer_overloaded_constraints_selects_concatenate_item_by_prefix_name() -> None:
    param_spec = ParamSpecType('P', 'P', TypeVarId(1), make_any(), make_any())
    ret_var = make_type_var('R', 2)
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))
    bool_type = make_instance(make_info('builtins.bool'))
    fallback = make_instance(make_info('function'))
    template = Overloaded([
        CallableType(
            [int_type, param_spec, param_spec],
            [ArgKind.NAMED, ArgKind.STAR, ArgKind.STAR2],
            ['other', None, None],
            ret_var,
            fallback,
            variables=[param_spec],
        ),
        CallableType(
            [int_type, param_spec, param_spec],
            [ArgKind.NAMED, ArgKind.STAR, ArgKind.STAR2],
            ['value', None, None],
            ret_var,
            fallback,
            variables=[param_spec],
        ),
    ])
    actual = CallableType(
        [int_type, str_type],
        [ArgKind.NAMED, ArgKind.NAMED_OPT],
        ['value', 'rest'],
        bool_type,
        fallback,
    )

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)
    solution = solve_constraints([ret_var, param_spec], constraints)

    assert solution[0] is bool_type
    assert isinstance(solution[1], Parameters)
    assert list(solution[1].arg_types) == [str_type]
    assert list(solution[1].arg_kinds) == [ArgKind.NAMED_OPT]
    assert list(solution[1].arg_names) == ['rest']


def test_infer_callable_concatenate_captures_optional_and_keyword_only_tail() -> None:
    param_spec = ParamSpecType('P', 'P', TypeVarId(1), make_any(), make_any())
    ret_var = make_type_var('R', 2)
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))
    bool_type = make_instance(make_info('builtins.bool'))
    bytes_type = make_instance(make_info('builtins.bytes'))
    fallback = make_instance(make_info('function'))
    template = _concatenate_callable(int_type, param_spec, ret_var, fallback)
    actual = CallableType(
        [int_type, str_type, bool_type, bytes_type],
        [ArgKind.POS, ArgKind.OPT, ArgKind.NAMED, ArgKind.NAMED_OPT],
        [None, None, 'flag', 'payload'],
        bool_type,
        fallback,
    )

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)
    solution = solve_constraints([ret_var, param_spec], constraints)

    assert solution[0] is bool_type
    assert isinstance(solution[1], Parameters)
    assert list(solution[1].arg_types) == [str_type, bool_type, bytes_type]
    assert list(solution[1].arg_kinds) == [ArgKind.OPT, ArgKind.NAMED, ArgKind.NAMED_OPT]
    assert list(solution[1].arg_names) == [None, 'flag', 'payload']


def test_solve_param_spec_constraints_reject_different_defaultish_parameter_shapes() -> None:
    param_spec = ParamSpecType('P', 'P', TypeVarId(1), make_any(), make_any())
    int_type = make_instance(make_info('builtins.int'))
    bool_type = make_instance(make_info('builtins.bool'))
    fallback = make_instance(make_info('function'))
    template = _param_spec_callable(param_spec, bool_type, fallback)
    required_actual = CallableType(
        [int_type],
        [ArgKind.NAMED],
        ['value'],
        bool_type,
        fallback,
    )
    optional_actual = CallableType(
        [int_type],
        [ArgKind.NAMED_OPT],
        ['value'],
        bool_type,
        fallback,
    )

    constraints = [
        *infer_constraints(template, required_actual, ConstraintOp.SUPERTYPE_OF),
        *infer_constraints(template, optional_actual, ConstraintOp.SUPERTYPE_OF),
    ]

    assert solve_constraints([param_spec], constraints) == [None]


def test_infer_overloaded_constraints_fail_closed_for_specific_and_param_spec_ambiguity() -> None:
    param_spec = ParamSpecType('P', 'P', TypeVarId(1), make_any(), make_any())
    ret_var = make_type_var('R', 2)
    int_type = make_instance(make_info('builtins.int'))
    fallback = make_instance(make_info('function'))
    template = Overloaded([
        CallableType([int_type], [ArgKind.POS], [None], int_type, fallback),
        _param_spec_callable(param_spec, ret_var, fallback),
    ])
    actual = _callable(int_type, int_type, fallback)

    with pytest.raises(UnsupportedTypeOperationError, match='2 matches'):
        infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)


def test_infer_overloaded_constraints_fails_closed_for_ambiguous_param_spec_items() -> None:
    left_param_spec = ParamSpecType('P', 'P', TypeVarId(1), make_any(), make_any())
    right_param_spec = ParamSpecType('Q', 'Q', TypeVarId(2), make_any(), make_any())
    ret_var = make_type_var('R', 3)
    int_type = make_instance(make_info('builtins.int'))
    bool_type = make_instance(make_info('builtins.bool'))
    fallback = make_instance(make_info('function'))
    template = Overloaded([
        _param_spec_callable(left_param_spec, ret_var, fallback),
        _param_spec_callable(right_param_spec, ret_var, fallback),
    ])
    actual = _callable(int_type, bool_type, fallback)

    with pytest.raises(UnsupportedTypeOperationError, match='2 matches'):
        infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)


def test_infer_callable_constraints_against_overloaded_actual_combines_all_items() -> None:
    t_var = make_type_var('T', 1)
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))
    fallback = make_instance(make_info('function'))
    template = _callable(int_type, t_var, fallback)  # type: ignore
    actual = Overloaded([
        _callable(int_type, int_type, fallback),
        _callable(int_type, str_type, fallback),
    ])

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)
    solution = solve_constraints([t_var], constraints)

    assert [(constraint.op, constraint.target) for constraint in constraints] == [
        (ConstraintOp.SUPERTYPE_OF, int_type),
        (ConstraintOp.SUPERTYPE_OF, str_type),
    ]
    assert [str(item) for item in solution] == ['Union[builtins.int, builtins.str]']


def test_infer_callable_constraints_against_overloaded_actual_uses_argument_contravariance() -> None:
    t_var = make_type_var('T', 1)
    object_info = make_info('builtins.object')
    int_info = make_info('builtins.int')
    str_info = make_info('builtins.str')
    int_info._mro = (int_info, object_info)
    str_info._mro = (str_info, object_info)
    object_type = make_instance(object_info)
    int_type = make_instance(int_info)
    str_type = make_instance(str_info)
    fallback = make_instance(make_info('function'))
    template = _callable(t_var, object_type, fallback)  # type: ignore
    actual = Overloaded([
        _callable(int_type, object_type, fallback),
        _callable(str_type, object_type, fallback),
    ])

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)
    solution = solve_constraints([t_var], constraints)

    assert [(constraint.op, constraint.target) for constraint in constraints] == [
        (ConstraintOp.SUBTYPE_OF, int_type),
        (ConstraintOp.SUBTYPE_OF, str_type),
    ]
    assert isinstance(solution[0], UninhabitedType)


def test_infer_callable_constraints_against_overloaded_actual_propagates_unsupported_items() -> None:
    t_var = make_type_var('T', 1)
    int_type = make_instance(make_info('builtins.int'))
    fallback = make_instance(make_info('function'))
    template = _callable(int_type, t_var, fallback)  # type: ignore
    actual = Overloaded([
        _callable(int_type, int_type, fallback),
        CallableType([int_type], [ArgKind.NAMED], ['value'], int_type, fallback),
    ])

    with pytest.raises(UnsupportedTypeOperationError, match='mismatched args'):
        infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)


def test_infer_overloaded_constraints_against_overloaded_actual_compares_ordered_items() -> None:
    t_var = make_type_var('T', 1)
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))
    bool_type = make_instance(make_info('builtins.bool'))
    fallback = make_instance(make_info('function'))
    template = Overloaded([
        CallableType([int_type], [ArgKind.POS], [None], t_var, fallback),
        CallableType([str_type], [ArgKind.POS], [None], t_var, fallback),
    ])
    actual = Overloaded([
        _callable(int_type, bool_type, fallback),
        _callable(str_type, int_type, fallback),
    ])

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)
    solution = solve_constraints([t_var], constraints)

    assert [(constraint.op, constraint.target) for constraint in constraints] == [
        (ConstraintOp.SUPERTYPE_OF, bool_type),
        (ConstraintOp.SUPERTYPE_OF, int_type),
    ]
    assert [str(item) for item in solution] == ['Union[builtins.bool, builtins.int]']


def test_infer_overloaded_constraints_against_overloaded_actual_uses_argument_contravariance() -> None:
    t_var = make_type_var('T', 1)
    object_info = make_info('builtins.object')
    int_info = make_info('builtins.int')
    str_info = make_info('builtins.str')
    int_info._mro = (int_info, object_info)
    str_info._mro = (str_info, object_info)
    object_type = make_instance(object_info)
    int_type = make_instance(int_info)
    str_type = make_instance(str_info)
    fallback = make_instance(make_info('function'))
    template = Overloaded([
        _callable(t_var, object_type, fallback),  # type: ignore[arg-type]
        _callable(t_var, object_type, fallback),  # type: ignore[arg-type]
    ])
    actual = Overloaded([
        _callable(int_type, object_type, fallback),
        _callable(str_type, object_type, fallback),
    ])

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)
    solution = solve_constraints([t_var], constraints)

    assert [(constraint.op, constraint.target) for constraint in constraints] == [
        (ConstraintOp.SUBTYPE_OF, int_type),
        (ConstraintOp.SUBTYPE_OF, str_type),
    ]
    assert isinstance(solution[0], UninhabitedType)


def test_infer_overloaded_constraints_against_overloaded_actual_fails_closed_for_item_count() -> None:
    int_type = make_instance(make_info('builtins.int'))
    fallback = make_instance(make_info('function'))
    left = Overloaded([
        _callable(int_type, int_type, fallback),
    ])
    right = Overloaded([
        _callable(int_type, int_type, fallback),
        _callable(int_type, int_type, fallback),
    ])

    with pytest.raises(UnsupportedTypeOperationError, match='mismatched item counts'):
        infer_constraints(left, right, ConstraintOp.SUPERTYPE_OF)


def test_infer_overloaded_constraints_against_overloaded_actual_fails_closed_for_item_shape() -> None:
    int_type = make_instance(make_info('builtins.int'))
    fallback = make_instance(make_info('function'))
    left = Overloaded([
        _callable(int_type, int_type, fallback),
    ])
    right = Overloaded([
        CallableType([int_type], [ArgKind.NAMED], ['value'], int_type, fallback),
    ])

    with pytest.raises(UnsupportedTypeOperationError, match='mismatched args'):
        infer_constraints(left, right, ConstraintOp.SUPERTYPE_OF)
