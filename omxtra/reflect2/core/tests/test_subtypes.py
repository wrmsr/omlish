# ruff: noqa: SLF001
import pytest

from ...errors import ReflectionError
from ...errors import UnsupportedTypeOperationError
from .. import symbols
from .. import types
from ..subtypes import get_base_args
from ..subtypes import get_base_args_or_none
from ..subtypes import get_base_instance
from ..subtypes import get_base_instance_or_none
from ..subtypes import get_mro_entries
from ..subtypes import get_mro_entries_or_none
from ..subtypes import get_mro_instances
from ..subtypes import get_mro_instances_or_none
from ..subtypes import is_alpha_structurally_equivalent
from ..subtypes import is_equivalent
from ..subtypes import is_same_type
from ..subtypes import is_structural_subtype
from ..subtypes import is_structurally_equivalent
from ..subtypes import is_subtype
from .helpers import make_any
from .helpers import make_info
from .helpers import make_instance
from .helpers import make_recursive_json_like_alias_case
from .helpers import make_recursive_variadic_tuple_alias_case
from .helpers import make_type_var
from .helpers import make_typed_dict


def test_same_type_instances_compare_typeinfo_identity_and_args() -> None:
    box_info = make_info('Box')
    other_box_info = make_info('Box')
    t_var = make_type_var('T', 1)

    assert is_same_type(make_instance(box_info, [t_var]), make_instance(box_info, [t_var]))
    assert not is_same_type(make_instance(box_info, [t_var]), make_instance(other_box_info, [t_var]))
    assert not is_same_type(make_instance(box_info, [t_var]), make_instance(box_info, [make_any()]))


def test_same_type_type_vars_compare_ids_not_names() -> None:
    assert is_same_type(make_type_var('T', 1), make_type_var('U', 1))
    assert not is_same_type(make_type_var('T', 1), make_type_var('T', 2))


def test_same_type_unions_are_order_insensitive() -> None:
    box_info = make_info('Box')
    left = types.UnionType([make_instance(box_info), types.NoneType(), make_any()])
    right = types.UnionType([make_any(), make_instance(box_info), types.NoneType()])

    assert is_same_type(left, right)
    assert is_equivalent(left, right)


def test_same_type_callables_compare_argument_shape() -> None:
    fn_info = make_info('function')
    fallback = make_instance(fn_info)
    a = make_instance(make_info('A'))
    b = make_instance(make_info('B'))

    left = types.CallableType([a], [symbols.ArgKind.POS], [None], b, fallback)
    same = types.CallableType([a], [symbols.ArgKind.POS], [None], b, fallback)
    different_name = types.CallableType([a], [symbols.ArgKind.POS], ['x'], b, fallback)

    assert is_same_type(left, same)
    assert not is_same_type(left, different_name)


def test_same_type_aliases_compare_alias_identity_and_args() -> None:
    t_var = make_type_var('T', 1)
    alias = symbols.TypeAlias('Alias', make_instance(make_info('Target'), [t_var]))
    other_alias = symbols.TypeAlias('Alias', make_instance(make_info('Target'), [t_var]))

    assert is_same_type(types.TypeAliasType(alias, [t_var]), types.TypeAliasType(alias, [t_var]))
    assert not is_same_type(types.TypeAliasType(alias, [t_var]), types.TypeAliasType(other_alias, [t_var]))


def test_same_type_wrappers_literals_and_typed_dicts() -> None:
    str_info = make_info('str')
    lit_left = types.LiteralType('x', make_instance(str_info))
    lit_right = types.LiteralType('x', make_instance(str_info))
    lit_other = types.LiteralType('y', make_instance(str_info))

    assert is_same_type(types.RequiredType(lit_left), types.RequiredType(lit_right))
    assert not is_same_type(types.RequiredType(lit_left), types.RequiredType(lit_other))
    assert not is_same_type(types.RequiredType(lit_left), types.RequiredType(lit_right, required=False))
    assert is_same_type(types.RequiredType(lit_left, required=False), types.RequiredType(lit_right, required=False))

    dict_info = make_info('dict')
    left_td = types.TypedDictType({'x': lit_left}, {'x'}, set(), make_instance(dict_info))
    right_td = types.TypedDictType({'x': lit_right}, {'x'}, set(), make_instance(dict_info))
    optional_td = types.TypedDictType({'x': lit_right}, set(), set(), make_instance(dict_info))

    assert is_same_type(left_td, right_td)
    assert not is_same_type(left_td, optional_td)


def test_alpha_equivalent_allows_different_type_var_ids_in_same_positions() -> None:
    from ..subtypes import is_alpha_equivalent

    box_info = make_info('Box')
    left = make_instance(box_info, [make_type_var('T', 1)])
    right = make_instance(box_info, [make_type_var('U', 2)])

    assert not is_same_type(left, right)
    assert is_alpha_equivalent(left, right)


def test_alpha_equivalent_requires_consistent_repeated_type_vars() -> None:
    from ..subtypes import is_alpha_equivalent

    pair_info = make_info('Pair')
    left_t = make_type_var('T', 1)
    right_t = make_type_var('T', 1)
    right_u = make_type_var('U', 2)

    left = make_instance(pair_info, [left_t, left_t])
    consistent = make_instance(pair_info, [right_u, right_u])
    inconsistent = make_instance(pair_info, [right_t, right_u])

    assert is_alpha_equivalent(left, consistent)
    assert not is_alpha_equivalent(left, inconsistent)


def test_alpha_equivalent_callable_argument_and_return_vars() -> None:
    from ..subtypes import is_alpha_equivalent

    fallback = make_instance(make_info('function'))
    left_t = make_type_var('T', 1)
    right_u = make_type_var('U', 2)
    right_v = make_type_var('V', 3)

    left = types.CallableType([left_t], [symbols.ArgKind.POS], [None], left_t, fallback)
    consistent = types.CallableType([right_u], [symbols.ArgKind.POS], [None], right_u, fallback)
    inconsistent = types.CallableType([right_u], [symbols.ArgKind.POS], [None], right_v, fallback)

    assert is_alpha_equivalent(left, consistent)
    assert not is_alpha_equivalent(left, inconsistent)


def make_type_var_tuple(name: str, raw_id: int) -> types.TypeVarTupleType:
    any_type = make_any()
    tuple_fallback = make_instance(make_info('builtins.tuple'), [any_type])
    return types.TypeVarTupleType(
        name,
        name,
        types.TypeVarId(raw_id),
        any_type,
        any_type,
        tuple_fallback,
    )


def test_alpha_structural_equivalent_allows_different_type_var_tuple_ids_in_same_positions() -> None:
    fallback = make_instance(make_info('builtins.tuple'), [make_any()])
    left_ts = make_type_var_tuple('Ts', 1)
    right_us = make_type_var_tuple('Us', 2)

    left = types.TupleType([types.UnpackType(left_ts)], fallback)
    right = types.TupleType([types.UnpackType(right_us)], fallback)

    assert not is_structurally_equivalent(left, right)
    assert is_alpha_structurally_equivalent(left, right)


def test_alpha_structural_equivalent_preserves_type_var_tuple_position_consistency() -> None:
    fallback = make_instance(make_info('builtins.tuple'), [make_any()])
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))
    left_ts = make_type_var_tuple('Ts', 1)
    right_us = make_type_var_tuple('Us', 2)
    right_vs = make_type_var_tuple('Vs', 3)

    left = types.TupleType([int_type, types.UnpackType(left_ts), str_type, types.UnpackType(left_ts)], fallback)
    consistent = types.TupleType([int_type, types.UnpackType(right_us), str_type, types.UnpackType(right_us)], fallback)
    inconsistent = types.TupleType(
        [int_type, types.UnpackType(right_us), str_type, types.UnpackType(right_vs)],
        fallback,
    )

    assert is_alpha_structurally_equivalent(left, consistent)
    assert not is_alpha_structurally_equivalent(left, inconsistent)


def test_same_type_overloads_preserve_item_order() -> None:
    fallback = make_instance(make_info('function'))
    int_type = make_instance(make_info('int'))
    str_type = make_instance(make_info('str'))

    int_item = types.CallableType([int_type], [symbols.ArgKind.POS], [None], int_type, fallback)
    str_item = types.CallableType([str_type], [symbols.ArgKind.POS], [None], str_type, fallback)

    assert is_same_type(types.Overloaded([int_item, str_item]), types.Overloaded([int_item, str_item]))
    assert not is_same_type(types.Overloaded([int_item, str_item]), types.Overloaded([str_item, int_item]))


def test_alpha_equivalent_overloads_canonicalize_type_vars_by_position() -> None:
    from ..subtypes import is_alpha_equivalent

    fallback = make_instance(make_info('function'))
    left_t = make_type_var('T', 1)
    left_u = make_type_var('U', 2)
    right_x = make_type_var('X', 3)
    right_y = make_type_var('Y', 4)

    left = types.Overloaded([
        types.CallableType([left_t], [symbols.ArgKind.POS], [None], left_t, fallback),
        types.CallableType([left_u], [symbols.ArgKind.POS], [None], left_u, fallback),
    ])
    right = types.Overloaded([
        types.CallableType([right_x], [symbols.ArgKind.POS], [None], right_x, fallback),
        types.CallableType([right_y], [symbols.ArgKind.POS], [None], right_y, fallback),
    ])
    inconsistent = types.Overloaded([
        types.CallableType([right_x], [symbols.ArgKind.POS], [None], right_y, fallback),
        types.CallableType([right_y], [symbols.ArgKind.POS], [None], right_y, fallback),
    ])

    assert is_alpha_equivalent(left, right)
    assert not is_alpha_equivalent(left, inconsistent)


def test_alpha_equivalent_still_checks_concrete_structure() -> None:
    from ..subtypes import is_alpha_equivalent

    t_var = make_type_var('T', 1)

    assert not is_alpha_equivalent(
        make_instance(make_info('Box'), [t_var]),
        make_instance(make_info('Other'), [t_var]),
    )


def make_recursive_alias(name: str, base: types.Type) -> types.TypeAliasType:
    alias = symbols.TypeAlias(name, base)
    alias_type = types.TypeAliasType(alias, [])
    alias._target = types.UnionType([base, alias_type])
    return alias_type


def test_alpha_equivalent_recursive_alias_is_equivalent_to_itself() -> None:
    from ..subtypes import is_alpha_equivalent

    alias_type = make_recursive_alias('A', types.NoneType())

    assert is_alpha_equivalent(alias_type, alias_type)


def test_alpha_equivalent_recursive_aliases_with_different_names() -> None:
    from ..subtypes import is_alpha_equivalent

    left = make_recursive_alias('A', types.NoneType())
    right = make_recursive_alias('B', types.NoneType())

    assert is_alpha_equivalent(left, right)


def test_alpha_equivalent_recursive_aliases_still_compare_targets() -> None:
    from ..subtypes import is_alpha_equivalent

    left = make_recursive_alias('A', types.NoneType())
    right = make_recursive_alias('B', make_any())

    assert not is_alpha_equivalent(left, right)


def test_alpha_equivalent_recursive_alias_backrefs_still_compare_args() -> None:
    from ..subtypes import is_alpha_equivalent

    list_info = make_info('builtins.list')
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))

    left_alias = symbols.TypeAlias('Left', make_any())
    right_alias = symbols.TypeAlias('Right', make_any())
    left_alias_type = types.TypeAliasType(left_alias, [])
    right_alias_type = types.TypeAliasType(right_alias, [])

    left_alias._target = make_instance(list_info, [types.TypeAliasType(left_alias, [int_type])])
    right_alias._target = make_instance(list_info, [types.TypeAliasType(right_alias, [str_type])])

    assert not is_alpha_equivalent(left_alias_type, right_alias_type)


def test_alpha_equivalent_parameterized_mutual_recursive_aliases() -> None:
    from ..subtypes import is_alpha_equivalent

    list_info = make_info('builtins.list')
    dict_info = make_info('builtins.dict')

    left_t = make_type_var('T', 1)
    left_u = make_type_var('U', 2)
    right_x = make_type_var('X', 3)
    right_y = make_type_var('Y', 4)

    left_a = symbols.TypeAlias('LeftA', make_any(), alias_tvars=[left_t])
    left_b = symbols.TypeAlias('LeftB', make_any(), alias_tvars=[left_u])
    right_a = symbols.TypeAlias('RightA', make_any(), alias_tvars=[right_x])
    right_b = symbols.TypeAlias('RightB', make_any(), alias_tvars=[right_y])

    left_a_type = types.TypeAliasType(left_a, [left_t])
    left_b_type = types.TypeAliasType(left_b, [left_u])
    right_a_type = types.TypeAliasType(right_a, [right_x])
    right_b_type = types.TypeAliasType(right_b, [right_y])

    left_a._target = make_instance(list_info, [left_b_type])
    left_b._target = make_instance(dict_info, [left_u, left_a_type])
    right_a._target = make_instance(list_info, [right_b_type])
    right_b._target = make_instance(dict_info, [right_y, right_a_type])

    assert is_alpha_equivalent(types.TypeAliasType(left_a, [left_t]), types.TypeAliasType(right_a, [right_x]))
    assert is_alpha_equivalent(types.TypeAliasType(left_b, [left_u]), types.TypeAliasType(right_b, [right_y]))


def test_alpha_equivalent_parameterized_mutual_recursive_aliases_reject_mismatched_backref_args() -> None:
    from ..subtypes import is_alpha_equivalent

    list_info = make_info('builtins.list')
    dict_info = make_info('builtins.dict')

    left_t = make_type_var('T', 1)
    left_u = make_type_var('U', 2)
    right_x = make_type_var('X', 3)
    right_y = make_type_var('Y', 4)

    left_a = symbols.TypeAlias('LeftA', make_any(), alias_tvars=[left_t])
    left_b = symbols.TypeAlias('LeftB', make_any(), alias_tvars=[left_u])
    right_a = symbols.TypeAlias('RightA', make_any(), alias_tvars=[right_x])
    right_b = symbols.TypeAlias('RightB', make_any(), alias_tvars=[right_y])

    left_a_type = types.TypeAliasType(left_a, [left_t])
    left_b_type = types.TypeAliasType(left_b, [left_u])
    right_b_type = types.TypeAliasType(right_b, [right_y])

    left_a._target = make_instance(list_info, [left_b_type])
    left_b._target = make_instance(dict_info, [left_u, left_a_type])
    right_a._target = make_instance(list_info, [right_b_type])
    right_b._target = make_instance(dict_info, [right_y, types.TypeAliasType(right_a, [right_y])])

    assert not is_alpha_equivalent(types.TypeAliasType(left_a, [left_t]), types.TypeAliasType(right_a, [right_x]))


def test_same_type_recursive_aliases_with_different_names_compare_structurally() -> None:
    left = make_recursive_alias('A', types.NoneType())
    right = make_recursive_alias('B', types.NoneType())

    assert is_same_type(left, left)
    assert is_same_type(left, right)


def test_structural_equivalent_expands_nonrecursive_aliases() -> None:
    list_info = make_info('builtins.list')
    int_type = make_instance(make_info('builtins.int'))
    target = make_instance(list_info, [int_type])
    alias = symbols.TypeAlias('Alias', target)

    assert not is_same_type(types.TypeAliasType(alias, []), target)
    assert is_structurally_equivalent(types.TypeAliasType(alias, []), target)


def test_structural_equivalent_ignores_annotated_around_alias_target() -> None:
    int_type = make_instance(make_info('builtins.int'))
    alias = symbols.TypeAlias('Alias', int_type)

    assert is_structurally_equivalent(
        types.AnnotatedType(types.TypeAliasType(alias, []), ('alias-md',)),
        types.AnnotatedType(int_type, ('target-md',)),
    )


def test_structural_equivalent_preserves_new_type_nominality_through_aliases() -> None:
    left_new_type = make_instance(make_info('NewType.UserId'))
    right_new_type = make_instance(make_info('NewType.AccountId'))
    left_alias = symbols.TypeAlias('LeftAlias', left_new_type)
    right_alias = symbols.TypeAlias('RightAlias', right_new_type)

    assert is_structurally_equivalent(types.TypeAliasType(left_alias, []), left_new_type)
    assert not is_structurally_equivalent(types.TypeAliasType(left_alias, []), right_new_type)
    assert not is_structurally_equivalent(types.TypeAliasType(left_alias, []), types.TypeAliasType(right_alias, []))


def test_structural_equivalent_recursive_alias_matches_one_unrolling() -> None:
    list_info = make_info('builtins.list')
    int_type = make_instance(make_info('builtins.int'))
    alias = symbols.TypeAlias('Node', make_any())
    alias_type = types.TypeAliasType(alias, [])
    alias._target = types.UnionType([int_type, make_instance(list_info, [alias_type])])

    assert is_structurally_equivalent(alias_type, alias.target)


def test_structural_equivalent_recursive_aliases_with_different_names() -> None:
    list_info = make_info('builtins.list')
    int_type = make_instance(make_info('builtins.int'))

    left_alias = symbols.TypeAlias('Left', make_any())
    right_alias = symbols.TypeAlias('Right', make_any())
    left_alias_type = types.TypeAliasType(left_alias, [])
    right_alias_type = types.TypeAliasType(right_alias, [])
    left_alias._target = types.UnionType([int_type, make_instance(list_info, [left_alias_type])])
    right_alias._target = types.UnionType([int_type, make_instance(list_info, [right_alias_type])])

    assert is_structurally_equivalent(left_alias_type, right_alias_type)


def test_structural_equivalent_recursive_aliases_reject_different_leaf() -> None:
    list_info = make_info('builtins.list')
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))

    left_alias = symbols.TypeAlias('Left', make_any())
    right_alias = symbols.TypeAlias('Right', make_any())
    left_alias_type = types.TypeAliasType(left_alias, [])
    right_alias_type = types.TypeAliasType(right_alias, [])
    left_alias._target = types.UnionType([int_type, make_instance(list_info, [left_alias_type])])
    right_alias._target = types.UnionType([str_type, make_instance(list_info, [right_alias_type])])

    assert not is_structurally_equivalent(left_alias_type, right_alias_type)


def test_alpha_structural_equivalent_parameterized_recursive_aliases() -> None:
    list_info = make_info('builtins.list')
    left_t = make_type_var('T', 1)
    right_u = make_type_var('U', 2)
    left_alias = symbols.TypeAlias('Left', make_any(), alias_tvars=[left_t])
    right_alias = symbols.TypeAlias('Right', make_any(), alias_tvars=[right_u])
    left_alias_type = types.TypeAliasType(left_alias, [left_t])
    right_alias_type = types.TypeAliasType(right_alias, [right_u])
    left_alias._target = make_instance(list_info, [left_alias_type])
    right_alias._target = make_instance(list_info, [right_alias_type])

    assert not is_structurally_equivalent(
        types.TypeAliasType(left_alias, [left_t]),
        types.TypeAliasType(right_alias, [right_u]),
    )
    assert is_alpha_structurally_equivalent(
        types.TypeAliasType(left_alias, [left_t]),
        types.TypeAliasType(right_alias, [right_u]),
    )


def test_structural_equivalent_recursive_variadic_tuple_alias_matches_one_unrolling() -> None:
    case = make_recursive_variadic_tuple_alias_case('TupleNode', 1)

    assert is_structurally_equivalent(case.concrete_alias_type, case.one_unrolling)


def test_alpha_structural_equivalent_recursive_variadic_tuple_aliases() -> None:
    left = make_recursive_variadic_tuple_alias_case('LeftTupleNode', 1)
    right = make_recursive_variadic_tuple_alias_case(
        'RightTupleNode',
        2,
        left.concrete_items,
        left.tuple_fallback,
    )

    assert not is_structurally_equivalent(left.alias_type, right.alias_type)
    assert is_alpha_structurally_equivalent(left.alias_type, right.alias_type)


def test_alpha_structural_equivalent_parameterized_mutual_recursive_aliases() -> None:
    list_info = make_info('builtins.list')
    dict_info = make_info('builtins.dict')

    left_t = make_type_var('T', 1)
    left_u = make_type_var('U', 2)
    right_x = make_type_var('X', 3)
    right_y = make_type_var('Y', 4)

    left_a = symbols.TypeAlias('LeftA', make_any(), alias_tvars=[left_t])
    left_b = symbols.TypeAlias('LeftB', make_any(), alias_tvars=[left_u])
    right_a = symbols.TypeAlias('RightA', make_any(), alias_tvars=[right_x])
    right_b = symbols.TypeAlias('RightB', make_any(), alias_tvars=[right_y])

    left_a_type = types.TypeAliasType(left_a, [left_t])
    left_b_type = types.TypeAliasType(left_b, [left_u])
    right_a_type = types.TypeAliasType(right_a, [right_x])
    right_b_type = types.TypeAliasType(right_b, [right_y])

    left_a._target = make_instance(list_info, [left_b_type])
    left_b._target = make_instance(dict_info, [left_u, left_a_type])
    right_a._target = make_instance(list_info, [right_b_type])
    right_b._target = make_instance(dict_info, [right_y, right_a_type])

    assert is_alpha_structurally_equivalent(
        types.TypeAliasType(left_a, [left_t]),
        types.TypeAliasType(right_a, [right_x]),
    )
    assert is_alpha_structurally_equivalent(
        types.TypeAliasType(left_b, [left_u]),
        types.TypeAliasType(right_b, [right_y]),
    )


def test_structural_subtype_expands_nonrecursive_aliases() -> None:
    int_type = make_instance(make_info('builtins.int'))
    alias = symbols.TypeAlias('Alias', int_type)

    with pytest.raises(UnsupportedTypeOperationError):
        is_subtype(types.TypeAliasType(alias, []), int_type)
    assert is_structural_subtype(types.TypeAliasType(alias, []), int_type)
    assert is_structural_subtype(int_type, types.TypeAliasType(alias, []))


def test_structural_subtype_ignores_annotated_around_alias_target() -> None:
    int_type = make_instance(make_info('builtins.int'))
    alias = symbols.TypeAlias('Alias', int_type)

    assert is_structural_subtype(types.AnnotatedType(types.TypeAliasType(alias, []), ('alias-md',)), int_type)
    assert is_structural_subtype(int_type, types.AnnotatedType(types.TypeAliasType(alias, []), ('alias-md',)))


def test_structural_subtype_preserves_new_type_nominality_through_aliases() -> None:
    int_type = make_instance(make_info('builtins.int'))
    left_info = make_info('example.UserId')
    right_info = make_info('example.AccountId')
    left_info._new_type_supertype = int_type
    right_info._new_type_supertype = int_type
    left_new_type = make_instance(left_info)
    right_new_type = make_instance(right_info)
    left_alias = symbols.TypeAlias('LeftAlias', left_new_type)
    right_alias = symbols.TypeAlias('RightAlias', right_new_type)

    assert is_structural_subtype(types.TypeAliasType(left_alias, []), left_new_type)
    assert not is_structural_subtype(types.TypeAliasType(left_alias, []), right_new_type)
    assert not is_structural_subtype(types.TypeAliasType(left_alias, []), types.TypeAliasType(right_alias, []))
    assert not is_structural_subtype(types.TypeAliasType(left_alias, []), int_type)


def test_structural_subtype_expands_literal_aliases_but_keeps_literal_directionality() -> None:
    str_type = make_instance(make_info('builtins.str'))
    literal = types.LiteralType('debug', str_type)
    literal_alias = symbols.TypeAlias('Mode', literal)

    assert is_structural_subtype(types.TypeAliasType(literal_alias, []), str_type)
    assert is_structural_subtype(types.TypeAliasType(literal_alias, []), literal)
    assert not is_structural_subtype(str_type, types.TypeAliasType(literal_alias, []))


def test_structural_subtype_compares_fixed_tuple_items() -> None:
    object_info = make_info('builtins.object')
    int_info = make_info('builtins.int')
    str_info = make_info('builtins.str')
    int_info._mro = [int_info, object_info]
    str_info._mro = [str_info, object_info]
    fallback = make_instance(make_info('builtins.tuple'), [make_any()])

    left = types.TupleType([make_instance(int_info), make_instance(str_info)], fallback)
    right = types.TupleType([make_instance(object_info), make_instance(object_info)], fallback)
    shorter = types.TupleType([make_instance(object_info)], fallback)

    assert is_structural_subtype(left, right)
    assert not is_structural_subtype(right, left)
    assert not is_structural_subtype(left, shorter)


def test_structural_subtype_expands_variadic_alias_to_fixed_tuple() -> None:
    fallback = make_instance(make_info('builtins.tuple'), [make_any()])
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))
    type_var_tuple = make_type_var_tuple('Ts', 1)
    alias = symbols.TypeAlias(
        'Alias',
        types.TupleType([types.UnpackType(type_var_tuple)], fallback),
        alias_tvars=[type_var_tuple],
    )
    alias_type = types.TypeAliasType(alias, [types.TupleType([int_type, str_type], fallback)])
    target = types.TupleType([int_type, str_type], fallback)

    assert is_structural_subtype(alias_type, target)
    assert is_structural_subtype(target, alias_type)


def test_structural_subtype_fails_closed_for_variadic_tuple_shapes() -> None:
    fallback = make_instance(make_info('builtins.tuple'), [make_any()])
    int_type = make_instance(make_info('builtins.int'))
    type_var_tuple = make_type_var_tuple('Ts', 1)
    variadic = types.TupleType([types.UnpackType(type_var_tuple)], fallback)
    concrete = types.TupleType([int_type], fallback)

    with pytest.raises(UnsupportedTypeOperationError, match='variadic Tuple subtype'):
        is_structural_subtype(variadic, concrete)

    with pytest.raises(UnsupportedTypeOperationError, match='variadic Tuple subtype'):
        is_structural_subtype(concrete, variadic)


def test_structural_subtype_recursive_alias_matches_one_unrolling_both_ways() -> None:
    list_info = make_info('builtins.list')
    int_type = make_instance(make_info('builtins.int'))
    alias = symbols.TypeAlias('Node', make_any())
    alias_type = types.TypeAliasType(alias, [])
    alias._target = types.UnionType([int_type, make_instance(list_info, [alias_type])])

    assert is_structural_subtype(alias_type, alias.target)
    assert is_structural_subtype(alias.target, alias_type)


def test_structural_subtype_json_like_recursive_alias_matches_one_unrolling_and_equivalent_alias() -> None:
    left = make_recursive_json_like_alias_case('Jsonish')
    right = make_recursive_json_like_alias_case(
        'OtherJsonish',
        reverse_union=True,
        list_info=left.list_info,
        dict_info=left.dict_info,
        bool_type=left.bool_type,
        int_type=left.int_type,
        str_type=left.str_type,
    )

    assert is_structurally_equivalent(left.alias_type, right.alias_type)
    assert is_structural_subtype(left.alias_type, left.one_unrolling)
    assert is_structural_subtype(left.one_unrolling, left.alias_type)
    assert is_structural_subtype(left.alias_type, right.alias_type)
    assert is_structural_subtype(right.alias_type, left.alias_type)


def test_structural_subtype_recursive_alias_containing_type_type_matches_one_unrolling() -> None:
    list_info = make_info('builtins.list')
    int_type = make_instance(make_info('builtins.int'))
    alias = symbols.TypeAlias('ClassNode', make_any())
    alias_type = types.TypeAliasType(alias, [])
    alias._target = types.UnionType([
        types.TypeType(int_type),
        types.TypeType(make_instance(list_info, [alias_type])),
    ])
    unrolled = types.UnionType([
        types.TypeType(int_type),
        types.TypeType(make_instance(list_info, [alias.target])),
    ])

    assert is_structural_subtype(alias_type, alias.target)
    assert is_structural_subtype(alias.target, alias_type)
    assert is_structural_subtype(alias_type, unrolled)
    assert is_structural_subtype(unrolled, alias_type)


def test_structural_subtype_recursive_union_is_directional() -> None:
    list_info = make_info('builtins.list')
    list_info._variances = [symbols.VarianceKind.CO]
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))

    left_alias = symbols.TypeAlias('Left', make_any())
    right_alias = symbols.TypeAlias('Right', make_any())
    left_alias_type = types.TypeAliasType(left_alias, [])
    right_alias_type = types.TypeAliasType(right_alias, [])
    left_alias._target = types.UnionType([int_type, make_instance(list_info, [left_alias_type])])
    right_alias._target = types.UnionType([int_type, str_type, make_instance(list_info, [right_alias_type])])

    assert is_structural_subtype(left_alias_type, right_alias_type)
    assert not is_structural_subtype(right_alias_type, left_alias_type)


def test_structural_subtype_recursive_alias_fails_closed_for_unsupported_callable_target() -> None:
    fallback = make_instance(make_info('function'))
    t_var = make_type_var('T', 1)
    other = make_instance(make_info('Other'))
    alias = symbols.TypeAlias('Fn', make_any())
    alias_type = types.TypeAliasType(alias, [])
    alias._target = types.CallableType([t_var], [symbols.ArgKind.POS], [None], alias_type, fallback, variables=[t_var])
    target = types.CallableType([other], [symbols.ArgKind.POS], [None], other, fallback)

    with pytest.raises(UnsupportedTypeOperationError, match='generic Callable'):
        is_structural_subtype(alias_type, target)


def test_structural_subtype_recursive_alias_fails_closed_for_unmapped_generic_base() -> None:
    base_info = make_info('Base')
    child_info = make_info('Child')
    child_info._mro = [child_info, base_info]
    int_type = make_instance(make_info('builtins.int'))
    alias = symbols.TypeAlias('ChildAlias', make_any())
    alias_type = types.TypeAliasType(alias, [])
    alias._target = types.UnionType([make_instance(child_info), alias_type])

    with pytest.raises(UnsupportedTypeOperationError, match='Generic base instance mapping'):
        is_structural_subtype(alias_type, make_instance(base_info, [int_type]))


def test_structural_subtype_respects_covariant_recursive_container_args() -> None:
    object_info = make_info('builtins.object')
    int_info = make_info('builtins.int')
    int_info._mro = [int_info, object_info]
    list_info = make_info('builtins.list')
    list_info._variances = [symbols.VarianceKind.CO]
    int_type = make_instance(int_info)
    object_type = make_instance(object_info)

    left_alias = symbols.TypeAlias('Left', make_any())
    right_alias = symbols.TypeAlias('Right', make_any())
    left_alias_type = types.TypeAliasType(left_alias, [])
    right_alias_type = types.TypeAliasType(right_alias, [])
    left_alias._target = make_instance(list_info, [types.UnionType([int_type, left_alias_type])])
    right_alias._target = make_instance(list_info, [types.UnionType([object_type, right_alias_type])])

    assert is_structural_subtype(left_alias_type, right_alias_type)
    assert not is_structural_subtype(right_alias_type, left_alias_type)


def test_callable_ellipsis_participates_in_same_type() -> None:
    fallback = make_instance(make_info('function'))
    any_type = make_any()
    left = types.CallableType([], [], [], any_type, fallback, is_ellipsis_args=True)
    right = types.CallableType([], [], [], any_type, fallback, is_ellipsis_args=False)

    assert not is_same_type(left, right)


def test_nominal_instance_subtype_uses_mro() -> None:
    object_info = make_info('object')
    int_info = make_info('int')
    int_info._mro = [int_info, object_info]

    assert is_subtype(make_instance(int_info), make_instance(object_info))
    assert not is_subtype(make_instance(object_info), make_instance(int_info))


def test_same_generic_instance_subtype_requires_same_args() -> None:
    box_info = make_info('Box')
    left = make_instance(box_info, [make_any()])
    right = make_instance(box_info, [make_any()])
    different = make_instance(box_info, [types.NoneType()])

    assert is_subtype(left, right)
    assert not is_subtype(left, different)


def test_same_overload_is_subtype_via_exact_type_match() -> None:
    fallback = make_instance(make_info('function'))
    int_type = make_instance(make_info('int'))
    str_type = make_instance(make_info('str'))
    overload = types.Overloaded([
        types.CallableType([int_type], [symbols.ArgKind.POS], [None], int_type, fallback),
        types.CallableType([str_type], [symbols.ArgKind.POS], [None], str_type, fallback),
    ])

    assert is_subtype(overload, overload)


def test_simple_callable_subtype_uses_contravariant_args_and_covariant_return() -> None:
    child, base = make_nominal_subtype_pair()
    fallback = make_instance(make_info('function'))

    left = types.CallableType([base], [symbols.ArgKind.POS], [None], child, fallback)
    right = types.CallableType([child], [symbols.ArgKind.POS], [None], base, fallback)

    assert is_subtype(left, right)
    assert not is_subtype(right, left)


def test_simple_callable_subtype_respects_argument_shape() -> None:
    item = make_instance(make_info('Item'))
    ret = make_instance(make_info('Ret'))
    fallback = make_instance(make_info('function'))

    positional = types.CallableType([item], [symbols.ArgKind.POS], [None], ret, fallback)
    named = types.CallableType([item], [symbols.ArgKind.NAMED], ['value'], ret, fallback)
    named_other = types.CallableType([item], [symbols.ArgKind.NAMED], ['other'], ret, fallback)

    assert not is_subtype(positional, named)
    assert not is_subtype(named, positional)
    assert not is_subtype(named, named_other)


def test_callable_subtype_allows_extra_optional_arguments_on_left() -> None:
    item = make_instance(make_info('Item'))
    ret = make_instance(make_info('Ret'))
    fallback = make_instance(make_info('function'))

    accepts_more = types.CallableType(
        [item, item],
        [symbols.ArgKind.POS, symbols.ArgKind.OPT],
        [None, None],
        ret,
        fallback,
    )
    required_only = types.CallableType([item], [symbols.ArgKind.POS], [None], ret, fallback)
    requires_more = types.CallableType(
        [item, item],
        [symbols.ArgKind.POS, symbols.ArgKind.POS],
        [None, None],
        ret,
        fallback,
    )

    assert is_subtype(accepts_more, required_only)
    assert not is_subtype(required_only, accepts_more)
    assert not is_subtype(requires_more, required_only)


def test_callable_subtype_allows_extra_optional_keyword_only_arguments_on_left() -> None:
    item = make_instance(make_info('Item'))
    ret = make_instance(make_info('Ret'))
    fallback = make_instance(make_info('function'))

    accepts_more = types.CallableType(
        [item, item],
        [symbols.ArgKind.POS, symbols.ArgKind.NAMED_OPT],
        [None, 'trace'],
        ret,
        fallback,
    )
    required_only = types.CallableType([item], [symbols.ArgKind.POS], [None], ret, fallback)
    requires_named = types.CallableType(
        [item, item],
        [symbols.ArgKind.POS, symbols.ArgKind.NAMED],
        [None, 'trace'],
        ret,
        fallback,
    )
    requires_other_named = types.CallableType(
        [item, item],
        [symbols.ArgKind.POS, symbols.ArgKind.NAMED],
        [None, 'other'],
        ret,
        fallback,
    )

    assert is_subtype(accepts_more, required_only)
    assert not is_subtype(required_only, accepts_more)
    assert is_subtype(accepts_more, requires_named)
    assert not is_subtype(accepts_more, requires_other_named)


def test_callable_ellipsis_subtype_uses_return_covariance_only() -> None:
    child, base = make_nominal_subtype_pair()
    fallback = make_instance(make_info('function'))

    left = types.CallableType([], [], [], child, fallback, is_ellipsis_args=True)
    right = types.CallableType([], [], [], base, fallback, is_ellipsis_args=True)

    assert is_subtype(left, right)
    assert not is_subtype(right, left)


def test_callable_subtype_with_variables_fails_closed_for_now() -> None:
    fallback = make_instance(make_info('function'))
    t_var = make_type_var('T', 1)
    other = make_instance(make_info('Other'))
    left = types.CallableType([t_var], [symbols.ArgKind.POS], [None], t_var, fallback, variables=[t_var])
    right = types.CallableType([t_var], [symbols.ArgKind.POS], [None], other, fallback)

    with pytest.raises(UnsupportedTypeOperationError, match='generic Callable'):
        is_subtype(left, right)


def test_callable_subtype_with_malformed_arg_metadata_fails_closed() -> None:
    fallback = make_instance(make_info('function'))
    int_type = make_instance(make_info('builtins.int'))
    left = types.CallableType([int_type], [], [], int_type, fallback)
    right = types.CallableType([int_type], [symbols.ArgKind.POS], [None], int_type, fallback)

    with pytest.raises(UnsupportedTypeOperationError, match='malformed Callable'):
        is_subtype(left, right)


def test_callable_subtype_with_param_spec_fails_closed_for_now() -> None:
    fallback = make_instance(make_info('function'))
    param_spec = types.ParamSpecType('P', 'P', types.TypeVarId(1), make_any(), make_any())
    ret = make_instance(make_info('Ret'))
    other = make_instance(make_info('Other'))
    left = types.CallableType(
        [param_spec, param_spec],
        [symbols.ArgKind.STAR, symbols.ArgKind.STAR2],
        [None, None],
        ret,
        fallback,
        variables=[param_spec],
    )
    right = types.CallableType(
        [param_spec, param_spec],
        [symbols.ArgKind.STAR, symbols.ArgKind.STAR2],
        [None, None],
        other,
        fallback,
        variables=[param_spec],
    )

    with pytest.raises(UnsupportedTypeOperationError, match='generic Callable'):
        is_subtype(left, right)


def test_different_overload_subtyping_compares_items_pairwise() -> None:
    fallback = make_instance(make_info('function'))
    int_type = make_instance(make_info('int'))
    str_type = make_instance(make_info('str'))
    left = types.Overloaded([
        types.CallableType([int_type], [symbols.ArgKind.POS], [None], int_type, fallback),
        types.CallableType([str_type], [symbols.ArgKind.POS], [None], str_type, fallback),
    ])
    right = types.Overloaded([
        types.CallableType([str_type], [symbols.ArgKind.POS], [None], str_type, fallback),
        types.CallableType([int_type], [symbols.ArgKind.POS], [None], int_type, fallback),
    ])

    assert not is_subtype(left, right)


def test_uninhabited_is_subtype_of_every_supported_type() -> None:
    int_type = make_instance(make_info('int'))
    never = types.UninhabitedType()

    assert is_subtype(never, int_type)
    assert not is_subtype(int_type, never)


def test_nominal_instance_subtype_does_not_map_generic_base_args_yet() -> None:
    base_info = make_info('Base')
    child_info = make_info('Child')
    child_info._mro = [child_info, base_info]

    child = make_instance(child_info)
    generic_base = make_instance(base_info, [make_any()])

    with pytest.raises(UnsupportedTypeOperationError):
        is_subtype(child, generic_base)


def make_nominal_subtype_pair() -> tuple[types.Instance, types.Instance]:
    base_info = make_info('Base')
    child_info = make_info('Child')
    child_info._mro = [child_info, base_info]
    return make_instance(child_info), make_instance(base_info)


def test_covariant_instance_subtype_uses_arg_subtyping() -> None:
    child, base = make_nominal_subtype_pair()
    box_info = symbols.TypeInfo('Box', 'Box', variances=[symbols.VarianceKind.CO])

    assert is_subtype(make_instance(box_info, [child]), make_instance(box_info, [base]))
    assert not is_subtype(make_instance(box_info, [base]), make_instance(box_info, [child]))


def test_contravariant_instance_subtype_uses_reversed_arg_subtyping() -> None:
    child, base = make_nominal_subtype_pair()
    sink_info = symbols.TypeInfo('Sink', 'Sink', variances=[symbols.VarianceKind.CONTRA])

    assert is_subtype(make_instance(sink_info, [base]), make_instance(sink_info, [child]))
    assert not is_subtype(make_instance(sink_info, [child]), make_instance(sink_info, [base]))


def test_invariant_instance_subtype_still_requires_same_arg() -> None:
    child, base = make_nominal_subtype_pair()
    box_info = symbols.TypeInfo('Box', 'Box', variances=[symbols.VarianceKind.IN])

    assert not is_subtype(make_instance(box_info, [child]), make_instance(box_info, [base]))
    assert is_subtype(make_instance(box_info, [child]), make_instance(box_info, [child]))


def test_missing_or_not_ready_variance_is_conservative() -> None:
    child, base = make_nominal_subtype_pair()
    missing_info = symbols.TypeInfo('Missing', 'Missing')
    not_ready_info = symbols.TypeInfo('NotReady', 'NotReady', variances=[symbols.VarianceKind.NOT_READY])

    assert not is_subtype(make_instance(missing_info, [child]), make_instance(missing_info, [base]))
    assert not is_subtype(make_instance(not_ready_info, [child]), make_instance(not_ready_info, [base]))


def test_typed_dict_subtype_allows_extra_source_keys() -> None:
    int_type = make_instance(make_info('int'))
    source = make_typed_dict({'x': int_type, 'y': int_type}, {'x', 'y'})
    target = make_typed_dict({'x': int_type}, {'x'})

    assert is_subtype(source, target)
    assert not is_subtype(target, source)


def test_typed_dict_subtype_allows_missing_optional_target_keys() -> None:
    int_type = make_instance(make_info('int'))
    source = make_typed_dict({'x': int_type}, {'x'})
    target = make_typed_dict({'x': int_type, 'maybe': int_type}, {'x'})

    assert is_subtype(source, target)


def test_typed_dict_subtype_requires_source_required_target_keys() -> None:
    int_type = make_instance(make_info('int'))
    source = make_typed_dict({'x': int_type}, set())
    target = make_typed_dict({'x': int_type}, {'x'})

    assert not is_subtype(source, target)


def test_typed_dict_mutable_items_are_invariant() -> None:
    child, base = make_nominal_subtype_pair()
    source = make_typed_dict({'x': child}, {'x'})
    target = make_typed_dict({'x': base}, {'x'})

    assert not is_subtype(source, target)
    assert is_subtype(source, make_typed_dict({'x': child}, {'x'}))


def test_typed_dict_readonly_target_items_are_covariant() -> None:
    child, base = make_nominal_subtype_pair()
    source = make_typed_dict({'x': child}, {'x'})
    target = make_typed_dict({'x': base}, {'x'}, {'x'})

    assert is_subtype(source, target)
    assert not is_subtype(target, source)


def test_typed_dict_readonly_source_does_not_satisfy_mutable_target() -> None:
    int_type = make_instance(make_info('int'))
    source = make_typed_dict({'x': int_type}, {'x'}, {'x'})
    target = make_typed_dict({'x': int_type}, {'x'})

    assert not is_subtype(source, target)


def test_typed_dict_required_source_satisfies_readonly_optional_target() -> None:
    int_type = make_instance(make_info('int'))
    source = make_typed_dict({'x': int_type}, {'x'})
    target = make_typed_dict({'x': int_type}, set(), {'x'})

    assert is_subtype(source, target)


def test_subtype_of_union_if_subtype_of_any_item() -> None:
    child, base = make_nominal_subtype_pair()
    other = make_instance(make_info('Other'))

    assert is_subtype(child, types.UnionType([other, base]))
    assert not is_subtype(other, types.UnionType([child, base]))


def test_union_subtype_if_all_items_subtype_of_right() -> None:
    child, base = make_nominal_subtype_pair()
    other = make_instance(make_info('Other'))

    assert is_subtype(types.UnionType([child, base]), base)
    assert not is_subtype(types.UnionType([child, other]), base)


def test_subtype_strips_type_guarded_and_annotated_wrappers() -> None:
    child, base = make_nominal_subtype_pair()

    assert is_subtype(types.TypeGuardedType(child), base)
    assert is_subtype(types.AnnotatedType(child, ('cfg',)), base)
    assert is_subtype(child, types.AnnotatedType(base, ('cfg',)))


def test_subtype_required_readonly_unpack_and_type_type_fail_closed_for_now() -> None:
    item = make_instance(make_info('Item'))
    target = make_instance(make_info('Target'))
    cases = [
        types.RequiredType(item),
        types.ReadOnlyType(item),
        types.UnpackType(item),
    ]

    for typ in cases:
        with pytest.raises(UnsupportedTypeOperationError, match='Unsupported subtype relation'):
            is_subtype(typ, target)


def test_type_type_subtype_uses_item_subtyping() -> None:
    child, base = make_nominal_subtype_pair()

    child_type = types.TypeType(child)
    base_type = types.TypeType(base)

    assert is_subtype(child_type, base_type)
    assert not is_subtype(base_type, child_type)


def test_type_type_subtype_preserves_any_and_uninhabited_item_behavior() -> None:
    any_type = make_any()
    never = types.UninhabitedType()
    item = make_instance(make_info('Item'))

    assert is_subtype(types.TypeType(any_type), types.TypeType(item))
    assert is_subtype(types.TypeType(item), types.TypeType(any_type))
    assert is_subtype(types.TypeType(never), types.TypeType(item))
    assert not is_subtype(types.TypeType(item), types.TypeType(never))


def test_type_type_subtype_fails_closed_for_unsupported_item_relation() -> None:
    fallback = make_instance(make_info('function'))
    callable_type = types.CallableType([], [], [], make_any(), fallback)
    item = make_instance(make_info('Item'))

    with pytest.raises(UnsupportedTypeOperationError, match='Unsupported subtype relation'):
        is_subtype(types.TypeType(callable_type), types.TypeType(item))


def test_type_type_subtype_to_non_type_type_still_fails_closed() -> None:
    item = make_instance(make_info('Item'))
    target = make_instance(make_info('Target'))

    with pytest.raises(UnsupportedTypeOperationError, match='Unsupported subtype relation'):
        is_subtype(types.TypeType(item), target)


def test_union_subtype_to_union_combines_union_rules() -> None:
    child, base = make_nominal_subtype_pair()
    other = make_instance(make_info('Other'))
    wider = types.UnionType([base, other])

    assert is_subtype(types.UnionType([child, other]), wider)
    assert not is_subtype(types.UnionType([base, other]), child)


def test_any_is_compatible_subtype_in_both_directions() -> None:
    any_type = make_any()
    int_type = make_instance(make_info('int'))

    assert is_subtype(any_type, int_type)
    assert is_subtype(int_type, any_type)


def test_unsupported_subtype_relation_raises() -> None:
    fallback = make_instance(make_info('function'))
    callable_type = types.CallableType([], [], [], make_any(), fallback)

    with pytest.raises(UnsupportedTypeOperationError):
        is_subtype(callable_type, make_instance(make_info('object')))


def test_same_type_unknown_type_subclass_raises() -> None:
    with pytest.raises(ReflectionError):
        is_same_type(types._TestingUnknownType(), types._TestingUnknownType())

    with pytest.raises(ReflectionError):
        is_same_type(types._TestingUnknownType(), make_any())


def test_alpha_equivalent_unknown_type_subclass_raises() -> None:
    from ..subtypes import is_alpha_equivalent

    with pytest.raises(ReflectionError):
        is_alpha_equivalent(types._TestingUnknownType(), types._TestingUnknownType())

    with pytest.raises(ReflectionError):
        is_alpha_equivalent(make_any(), types._TestingUnknownType())


def test_is_subtype_or_false_returns_false_for_unsupported_relations() -> None:
    from ..subtypes import is_subtype_or_false

    fallback = make_instance(make_info('function'))
    callable_type = types.CallableType([], [], [], make_any(), fallback)

    assert not is_subtype_or_false(callable_type, make_instance(make_info('object')))


def test_is_subtype_or_false_returns_strict_result_when_supported() -> None:
    from ..subtypes import is_subtype_or_false

    child, base = make_nominal_subtype_pair()

    assert is_subtype_or_false(child, base)


def test_nominal_instance_subtype_maps_direct_generic_base_args() -> None:
    any_type = make_any()
    t_var = types.TypeVarType(
        'T',
        'T',
        types.TypeVarId(1),
        [],
        any_type,
        any_type,
    )
    base_info = symbols.TypeInfo('Base', 'Base', variances=[symbols.VarianceKind.IN])
    child_info = symbols.TypeInfo(
        'Child',
        'Child',
        bases=[types.Instance(base_info, [t_var])],
        type_vars=[t_var],
    )
    child_info._mro = [child_info, base_info]
    int_type = make_instance(make_info('int'))
    str_type = make_instance(make_info('str'))

    assert is_subtype(make_instance(child_info, [int_type]), make_instance(base_info, [int_type]))
    assert not is_subtype(make_instance(child_info, [int_type]), make_instance(base_info, [str_type]))


def test_nominal_instance_subtype_maps_direct_concrete_base_args() -> None:
    base_info = symbols.TypeInfo('Base', 'Base', variances=[symbols.VarianceKind.IN])
    int_type = make_instance(make_info('int'))
    str_type = make_instance(make_info('str'))
    child_info = symbols.TypeInfo('Child', 'Child', bases=[types.Instance(base_info, [int_type])])
    child_info._mro = [child_info, base_info]

    assert is_subtype(make_instance(child_info), make_instance(base_info, [int_type]))
    assert not is_subtype(make_instance(child_info), make_instance(base_info, [str_type]))


def test_nominal_instance_subtype_maps_indirect_generic_base_args() -> None:
    base_info = symbols.TypeInfo('Base', 'Base', variances=[symbols.VarianceKind.IN])
    middle_t = make_type_var('T', 1)
    middle_info = symbols.TypeInfo(
        'Middle',
        'Middle',
        bases=[types.Instance(base_info, [middle_t])],
        type_vars=[middle_t],
    )
    child_t = make_type_var('U', 2)
    child_info = symbols.TypeInfo(
        'Child',
        'Child',
        bases=[types.Instance(middle_info, [child_t])],
        type_vars=[child_t],
    )
    child_info._mro = [child_info, middle_info, base_info]
    int_type = make_instance(make_info('int'))
    str_type = make_instance(make_info('str'))

    assert is_subtype(make_instance(child_info, [int_type]), make_instance(base_info, [int_type]))
    assert not is_subtype(make_instance(child_info, [int_type]), make_instance(base_info, [str_type]))


def test_nominal_instance_subtype_maps_indirect_concrete_base_args() -> None:
    base_info = symbols.TypeInfo('Base', 'Base', variances=[symbols.VarianceKind.IN])
    int_type = make_instance(make_info('int'))
    str_type = make_instance(make_info('str'))
    middle_info = symbols.TypeInfo('Middle', 'Middle', bases=[types.Instance(base_info, [int_type])])
    child_info = symbols.TypeInfo('Child', 'Child', bases=[types.Instance(middle_info, [])])
    child_info._mro = [child_info, middle_info, base_info]

    assert is_subtype(make_instance(child_info), make_instance(base_info, [int_type]))
    assert not is_subtype(make_instance(child_info), make_instance(base_info, [str_type]))


def test_nominal_instance_subtype_still_raises_for_unmapped_generic_base() -> None:
    base_info = make_info('Base')
    middle_info = make_info('Middle')
    child_info = make_info('Child')
    child_info._bases = [types.Instance(middle_info, [])]
    child_info._mro = [child_info, middle_info, base_info]

    with pytest.raises(UnsupportedTypeOperationError):
        is_subtype(make_instance(child_info), make_instance(base_info, [make_any()]))


def test_get_base_instance_returns_self_for_same_type() -> None:
    info = make_info('Thing')
    instance = make_instance(info, [make_any()])

    assert get_base_instance(instance, info) is instance


def test_get_base_instance_returns_none_for_missing_base() -> None:
    left_info = make_info('Left')
    right_info = make_info('Right')

    assert get_base_instance(make_instance(left_info), right_info) is None


def test_get_base_instance_maps_direct_generic_base_args() -> None:
    base_info = symbols.TypeInfo('Base', 'Base', variances=[symbols.VarianceKind.IN])
    t_var = make_type_var('T', 1)
    child_info = symbols.TypeInfo(
        'Child',
        'Child',
        bases=[types.Instance(base_info, [t_var])],
        type_vars=[t_var],
    )
    child_info._mro = [child_info, base_info]
    int_type = make_instance(make_info('int'))

    mapped = get_base_instance(make_instance(child_info, [int_type]), base_info)

    assert isinstance(mapped, types.Instance)
    assert mapped.type is base_info
    assert mapped.args == [int_type]


def test_get_base_instance_maps_indirect_generic_base_args() -> None:
    base_info = symbols.TypeInfo('Base', 'Base', variances=[symbols.VarianceKind.IN])
    middle_t = make_type_var('T', 1)
    middle_info = symbols.TypeInfo(
        'Middle',
        'Middle',
        bases=[types.Instance(base_info, [middle_t])],
        type_vars=[middle_t],
    )
    child_t = make_type_var('U', 2)
    child_info = symbols.TypeInfo(
        'Child',
        'Child',
        bases=[types.Instance(middle_info, [child_t])],
        type_vars=[child_t],
    )
    child_info._mro = [child_info, middle_info, base_info]
    int_type = make_instance(make_info('int'))

    mapped = get_base_instance(make_instance(child_info, [int_type]), base_info)

    assert isinstance(mapped, types.Instance)
    assert mapped.type is base_info
    assert mapped.args == [int_type]


def test_get_mro_instances_maps_each_generic_layer() -> None:
    base_info = symbols.TypeInfo('Base', 'Base', variances=[symbols.VarianceKind.IN, symbols.VarianceKind.IN])
    middle_t = make_type_var('T', 1)
    middle_info = symbols.TypeInfo(
        'Middle',
        'Middle',
        bases=[types.Instance(base_info, [types.Instance(make_info('list'), [middle_t]), types.NoneType()])],
        type_vars=[middle_t],
    )
    child_t = make_type_var('U', 2)
    child_info = symbols.TypeInfo(
        'Child',
        'Child',
        bases=[types.Instance(middle_info, [child_t])],
        type_vars=[child_t],
    )
    child_info._mro = [child_info, middle_info, base_info]
    int_type = make_instance(make_info('int'))

    instances = get_mro_instances(make_instance(child_info, [int_type]))

    assert [instance.type.name for instance in instances] == ['Child', 'Middle', 'Base']
    assert [str(arg) for arg in instances[0].args] == ['int']
    assert [str(arg) for arg in instances[1].args] == ['int']
    assert [str(arg) for arg in instances[2].args] == ['list[int]', 'None']


def test_get_mro_instances_or_none_returns_mapped_instances() -> None:
    base_info = symbols.TypeInfo('Base', 'Base')
    child_info = symbols.TypeInfo('Child', 'Child', bases=[types.Instance(base_info, [])])
    child_info._mro = [child_info, base_info]

    instances = get_mro_instances_or_none(make_instance(child_info))

    assert instances is not None
    assert [instance.type.name for instance in instances] == ['Child', 'Base']


def test_get_mro_instances_or_none_suppresses_unsupported_mapping() -> None:
    base_t = make_type_var('T', 1)
    base_info = symbols.TypeInfo('Base', 'Base', type_vars=[base_t])
    middle_info = make_info('Middle')
    child_info = make_info('Child')
    child_info._bases = [types.Instance(middle_info, [])]
    child_info._mro = [child_info, middle_info, base_info]

    assert get_mro_instances_or_none(make_instance(child_info)) is None


def test_get_mro_entries_exposes_info_instance_and_args() -> None:
    base_info = symbols.TypeInfo('Base', 'Base', variances=[symbols.VarianceKind.IN])
    t_var = make_type_var('T', 1)
    child_info = symbols.TypeInfo(
        'Child',
        'Child',
        bases=[types.Instance(base_info, [t_var])],
        type_vars=[t_var],
    )
    child_info._mro = [child_info, base_info]
    int_type = make_instance(make_info('int'))

    entries = get_mro_entries(make_instance(child_info, [int_type]))

    assert [entry.info.name for entry in entries] == ['Child', 'Base']
    assert [str(entry.instance) for entry in entries] == ['Child[int]', 'Base[int]']
    assert [[str(arg) for arg in entry.args] for entry in entries] == [['int'], ['int']]


def test_get_mro_entries_or_none_suppresses_unsupported_mapping() -> None:
    base_t = make_type_var('T', 1)
    base_info = symbols.TypeInfo('Base', 'Base', type_vars=[base_t])
    child_info = make_info('Child')
    child_info._mro = [child_info, base_info]

    assert get_mro_entries_or_none(make_instance(child_info)) is None


def test_get_base_instance_synthesizes_unparameterized_nominal_base() -> None:
    base_info = make_info('Base')
    child_info = make_info('Child')
    child_info._mro = [child_info, base_info]

    mapped = get_base_instance(make_instance(child_info), base_info)

    assert isinstance(mapped, types.Instance)
    assert mapped.type is base_info
    assert mapped.args == []


def test_get_base_instance_raises_for_unmapped_generic_base() -> None:
    base_t = make_type_var('T', 1)
    base_info = symbols.TypeInfo('Base', 'Base', type_vars=[base_t])
    middle_info = make_info('Middle')
    child_info = make_info('Child')
    child_info._bases = [types.Instance(middle_info, [])]
    child_info._mro = [child_info, middle_info, base_info]

    with pytest.raises(UnsupportedTypeOperationError):
        get_base_instance(make_instance(child_info), base_info)


def test_get_base_instance_or_none_returns_mapped_base() -> None:
    base_info = symbols.TypeInfo('Base', 'Base', variances=[symbols.VarianceKind.IN])
    t_var = make_type_var('T', 1)
    child_info = symbols.TypeInfo(
        'Child',
        'Child',
        bases=[types.Instance(base_info, [t_var])],
        type_vars=[t_var],
    )
    child_info._mro = [child_info, base_info]
    int_type = make_instance(make_info('int'))

    mapped = get_base_instance_or_none(make_instance(child_info, [int_type]), base_info)

    assert isinstance(mapped, types.Instance)
    assert mapped.type is base_info
    assert mapped.args == [int_type]


def test_get_base_instance_or_none_returns_none_for_missing_base() -> None:
    left_info = make_info('Left')
    right_info = make_info('Right')

    assert get_base_instance_or_none(make_instance(left_info), right_info) is None


def test_get_base_instance_or_none_suppresses_unsupported_mapping() -> None:
    base_t = make_type_var('T', 1)
    base_info = symbols.TypeInfo('Base', 'Base', type_vars=[base_t])
    middle_info = make_info('Middle')
    child_info = make_info('Child')
    child_info._bases = [types.Instance(middle_info, [])]
    child_info._mro = [child_info, middle_info, base_info]

    assert get_base_instance_or_none(make_instance(child_info), base_info) is None


def test_get_base_args_returns_mapped_direct_generic_base_args() -> None:
    base_info = symbols.TypeInfo('Base', 'Base', variances=[symbols.VarianceKind.IN])
    t_var = make_type_var('T', 1)
    child_info = symbols.TypeInfo(
        'Child',
        'Child',
        bases=[types.Instance(base_info, [t_var])],
        type_vars=[t_var],
    )
    child_info._mro = [child_info, base_info]
    int_type = make_instance(make_info('int'))

    args = get_base_args(make_instance(child_info, [int_type]), base_info)

    assert args == [int_type]


def test_get_base_args_returns_none_for_missing_base() -> None:
    left_info = make_info('Left')
    right_info = make_info('Right')

    assert get_base_args(make_instance(left_info), right_info) is None


def test_get_base_args_returns_same_instance_args_for_same_type() -> None:
    info = make_info('Box')
    int_type = make_instance(make_info('int'))

    args = get_base_args(make_instance(info, [int_type]), info)

    assert args == [int_type]


def test_get_base_args_or_none_returns_args_when_mappable() -> None:
    base_info = symbols.TypeInfo('Base', 'Base', variances=[symbols.VarianceKind.IN])
    t_var = make_type_var('T', 1)
    child_info = symbols.TypeInfo(
        'Child',
        'Child',
        bases=[types.Instance(base_info, [t_var])],
        type_vars=[t_var],
    )
    child_info._mro = [child_info, base_info]
    int_type = make_instance(make_info('int'))

    args = get_base_args_or_none(make_instance(child_info, [int_type]), base_info)

    assert args == [int_type]


def test_get_base_args_or_none_returns_none_for_missing_base() -> None:
    left_info = make_info('Left')
    right_info = make_info('Right')

    assert get_base_args_or_none(make_instance(left_info), right_info) is None


def test_get_base_args_or_none_suppresses_unsupported_mapping() -> None:
    base_t = make_type_var('T', 1)
    base_info = symbols.TypeInfo('Base', 'Base', type_vars=[base_t])
    middle_info = make_info('Middle')
    child_info = make_info('Child')
    child_info._bases = [types.Instance(middle_info, [])]
    child_info._mro = [child_info, middle_info, base_info]

    assert get_base_args_or_none(make_instance(child_info), base_info) is None
