# ruff: noqa: SLF001
import typing as ta

import pytest

from ...errors import UnsupportedTypeOperationError
from ..constraints import ConstraintOp
from ..constraints import infer_constraints
from ..solve import solve_constraints
from ..strconv import type_str
from ..symbols import TypeAlias
from ..symbols import TypeInfo
from ..symbols import VarianceKind
from ..types import Instance
from ..types import LiteralType
from ..types import NoneType
from ..types import TupleType
from ..types import Type
from ..types import TypeAliasType
from ..types import UnionType
from .helpers import make_any
from .helpers import make_info
from .helpers import make_instance
from .helpers import make_type_var


def _literal(value: object, fullname: str) -> LiteralType:
    return LiteralType(ta.cast(ta.Any, value), make_instance(make_info(fullname)))


def test_infer_constraints_rejects_mismatched_literal_leaves() -> None:
    with pytest.raises(UnsupportedTypeOperationError, match='concrete leaf'):
        infer_constraints(
            _literal('left', 'builtins.str'),
            _literal('right', 'builtins.str'),
            ConstraintOp.SUPERTYPE_OF,
        )


def test_infer_constraints_solves_type_var_to_literal_value() -> None:
    t_var = make_type_var('T', 1)
    literal = _literal('debug', 'builtins.str')

    constraints = infer_constraints(t_var, literal, ConstraintOp.SUPERTYPE_OF)

    assert solve_constraints([t_var], constraints) == [literal]


def test_infer_union_constraints_matches_literal_tag_and_solves_payload() -> None:
    t_var = make_type_var('T', 1)
    tag = _literal('ok', 'builtins.str')
    payload = _literal('active', 'builtins.str')
    fallback = make_instance(make_info('builtins.tuple'), [make_any()])

    constraints = infer_constraints(
        UnionType([tag, TupleType([t_var], fallback)]),
        UnionType([TupleType([payload], fallback), tag]),
        ConstraintOp.SUPERTYPE_OF,
    )

    assert solve_constraints([t_var], constraints) == [payload]


def test_infer_generic_constraints_preserve_new_type_identity() -> None:
    t_var = make_type_var('T', 1)
    user_id = Instance(TypeInfo('UserId', 'example.UserId'), [])
    account_id = Instance(TypeInfo('AccountId', 'example.AccountId'), [])
    box_info = TypeInfo('Box', 'Box', type_vars=[t_var], variances=[VarianceKind.CO])

    constraints = infer_constraints(
        Instance(box_info, [t_var]),
        Instance(box_info, [user_id]),
        ConstraintOp.SUPERTYPE_OF,
    )
    solution = solve_constraints([t_var], constraints)

    assert solution == [user_id]
    assert solution != [account_id]
    assert type_str(ta.cast(Type, solution[0])) == 'example.UserId'


def test_infer_alias_constraints_preserve_new_type_literal_shape() -> None:
    t_var = make_type_var('T', 1)
    mode = Instance(TypeInfo('Mode', 'example.Mode'), [])
    alias = TypeAlias(
        'MaybeBox',
        UnionType([
            Instance(
                TypeInfo(
                    'Box',
                    'Box',
                    type_vars=[t_var],
                    variances=[VarianceKind.CO],
                ),
                [t_var],
            ),
            NoneType(),
        ]),
        alias_tvars=[t_var],
    )
    target = ta.cast(Instance, ta.cast(UnionType, alias.target).items[0])

    constraints = infer_constraints(
        TypeAliasType(alias, [t_var]),
        UnionType([NoneType(), Instance(target.type, [mode])]),
        ConstraintOp.SUPERTYPE_OF,
    )

    assert solve_constraints([t_var], constraints) == [mode]
