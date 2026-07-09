# ruff: noqa: SLF001
import typing as ta

from ..core.constraints import ConstraintOp
from ..core.constraints import infer_constraints
from ..core.solve import solve_constraints
from ..core.strconv import type_str
from ..core.types import Instance
from ..core.types import LiteralType
from ..core.types import TupleType
from ..core.types import Type
from ..core.types import TypeAliasType
from ..core.types import TypeVarLikeType
from ..core.types import UnionType
from .helpers import make_mirror


def test_runtime_constraints_preserve_reflected_newtype_identity() -> None:
    t_var = ta.TypeVar('T')  # type: ignore  # noqa
    user_id = ta.NewType('UserId', int)  # type: ignore  # noqa
    account_id = ta.NewType('AccountId', int)  # type: ignore  # noqa
    mirror = make_mirror()
    template = mirror.reflect_type(list[t_var])  # type: ignore
    actual = mirror.reflect_type(list[user_id])
    account_type = mirror.reflect_type(account_id)

    assert isinstance(template, Instance)
    assert isinstance(template.args[0], TypeVarLikeType)

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)
    solution = solve_constraints([template.args[0]], constraints)

    assert solution != [account_type]
    assert type_str(ta.cast(Type, solution[0])).endswith('.UserId')


def test_runtime_constraints_preserve_newtype_inside_actual_alias() -> None:
    t_var = ta.TypeVar('T')  # type: ignore  # noqa
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore  # noqa
    mode_list = ta.TypeAliasType('ModeList', list[mode])  # type: ignore
    mirror = make_mirror()
    template = mirror.reflect_type(list[t_var])  # type: ignore
    actual = mirror.reflect_type(mode_list)

    assert isinstance(template, Instance)
    assert isinstance(actual, TypeAliasType)
    assert isinstance(template.args[0], TypeVarLikeType)

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)
    solution = solve_constraints([template.args[0]], constraints)

    assert type_str(ta.cast(Type, solution[0])).endswith('.Mode')


def test_runtime_constraints_solve_nested_collection_to_newtype_literal_item() -> None:
    t_var = ta.TypeVar('T')  # type: ignore  # noqa
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore  # noqa
    mode_map = ta.TypeAliasType('ModeMap', ta.Mapping[str, list[mode]])  # type: ignore
    mirror = make_mirror()
    template = mirror.reflect_type(ta.Mapping[str, list[t_var]])  # type: ignore
    actual = mirror.reflect_type(mode_map)

    assert isinstance(template, Instance)
    assert isinstance(actual, TypeAliasType)
    item_template = template.args[1]
    assert isinstance(item_template, Instance)
    item_type_var = item_template.args[0]
    assert isinstance(item_type_var, TypeVarLikeType)

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)
    solution = solve_constraints([item_type_var], constraints)

    assert type_str(ta.cast(Type, solution[0])).endswith('.Mode')


def test_runtime_constraints_solve_type_var_to_literal_value() -> None:
    t_var = ta.TypeVar('T')  # type: ignore  # noqa
    mirror = make_mirror()
    template = mirror.reflect_type(list[t_var])  # type: ignore
    actual = mirror.reflect_type(list[ta.Literal['active']])

    assert isinstance(template, Instance)
    assert isinstance(template.args[0], TypeVarLikeType)

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)
    solution = solve_constraints([template.args[0]], constraints)

    assert isinstance(solution[0], LiteralType)
    assert solution[0].value == 'active'


def test_runtime_constraints_match_literal_tagged_union_and_solve_payload() -> None:
    t_var = ta.TypeVar('T')  # type: ignore  # noqa
    mirror = make_mirror()
    template = mirror.reflect_type(ta.Literal['ok'] | tuple[t_var])  # type: ignore
    actual = mirror.reflect_type(tuple[ta.Literal['active']] | ta.Literal['ok'])

    assert isinstance(template, UnionType)
    tuple_template = next(item for item in template.items if isinstance(item, TupleType))
    assert isinstance(tuple_template.items[0], TypeVarLikeType)

    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)
    solution = solve_constraints([tuple_template.items[0]], constraints)

    assert isinstance(solution[0], LiteralType)
    assert solution[0].value == 'active'
