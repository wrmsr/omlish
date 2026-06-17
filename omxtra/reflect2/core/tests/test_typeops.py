# ruff: noqa: PLC0132 SLF001
import typing as ta

import pytest

from ...errors import ReflectionError
from ...reflect import RuntimeTypeReflector
from ...universe import RuntimeTypeUniverse
from .. import symbols
from .. import typeops
from .. import types


def make_any() -> types.AnyType:
    return types.AnyType(types.TypeOfAny.EXPLICIT)


def make_type_var(name: str = 'T') -> types.TypeVarType:
    any_type = make_any()
    return types.TypeVarType(
        name,
        name,
        types.TypeVarId(1),
        [],
        any_type,
        any_type,
    )


def test_get_proper_type_expands_aliases() -> None:
    target = types.UnionType([types.NoneType(), make_any()])
    alias = symbols.TypeAlias('Alias', target)
    alias_type = types.TypeAliasType(alias, [])

    assert typeops.get_proper_type(alias_type) is target
    assert typeops.get_proper_type(types.TypeGuardedType(alias_type)) is target


def test_has_type_vars_detects_nested_type_vars() -> None:
    info = symbols.TypeInfo('Box', 'Box')

    assert typeops.has_type_vars(types.Instance(info, [make_type_var()]))
    assert not typeops.has_type_vars(types.Instance(info, [make_any()]))


def test_has_type_vars_does_not_expand_alias_targets() -> None:
    alias = symbols.TypeAlias('Alias', types.Instance(symbols.TypeInfo('Box'), [make_type_var()]))

    assert not typeops.has_type_vars(types.TypeAliasType(alias, []))
    assert typeops.has_type_vars(types.TypeAliasType(alias, [make_type_var('U')]))


def test_flatten_nested_unions() -> None:
    left = types.NoneType()
    middle = make_any()
    right = types.Instance(symbols.TypeInfo('Box'), [])
    union = types.UnionType([left, types.UnionType([middle, right])])

    assert typeops.flatten_nested_unions([union]) == [left, middle, right]


def test_make_union_collapses_single_item() -> None:
    item = make_any()

    assert typeops.make_union([item]) is item

    union = typeops.make_union([types.NoneType(), item])
    assert isinstance(union, types.UnionType)
    assert len(union.items) == 2


def test_collect_aliases_follows_alias_targets() -> None:
    target_alias = symbols.TypeAlias('TargetAlias', types.NoneType())
    wrapper_alias = symbols.TypeAlias('WrapperAlias', types.TypeAliasType(target_alias, []))

    aliases = typeops.collect_aliases(types.TypeAliasType(wrapper_alias, []))

    assert wrapper_alias in aliases
    assert target_alias in aliases


def test_type_alias_type_reports_non_recursive_alias() -> None:
    alias = symbols.TypeAlias('Alias', types.UnionType([types.NoneType(), make_any()]))

    assert not types.TypeAliasType(alias, []).is_recursive


def test_type_alias_type_reports_direct_recursive_alias() -> None:
    alias = symbols.TypeAlias('Recur', make_any())
    alias_type = types.TypeAliasType(alias, [])
    alias._target = types.UnionType([types.NoneType(), alias_type])

    assert alias_type.is_recursive


def test_type_alias_type_reports_indirect_recursive_alias_cycle() -> None:
    alias_a = symbols.TypeAlias('A', make_any())
    alias_b = symbols.TypeAlias('B', make_any())
    alias_a._target = types.TypeAliasType(alias_b, [])
    alias_b._target = types.UnionType([types.NoneType(), types.TypeAliasType(alias_a, [])])

    assert types.TypeAliasType(alias_a, []).is_recursive
    assert types.TypeAliasType(alias_b, []).is_recursive


def test_flatten_nested_unions_can_preserve_recursive_aliases() -> None:
    alias = symbols.TypeAlias('Recur', make_any())
    alias_type = types.TypeAliasType(alias, [])
    alias._target = types.UnionType([types.NoneType(), alias_type])

    assert typeops.flatten_nested_unions([alias_type], handle_recursive=False) == [alias_type]


def test_flatten_nested_unions_expands_non_recursive_aliases() -> None:
    none_type = types.NoneType()
    any_type = make_any()
    alias = symbols.TypeAlias('Alias', types.UnionType([none_type, any_type]))

    assert typeops.flatten_nested_unions([types.TypeAliasType(alias, [])]) == [none_type, any_type]


def test_get_proper_type_expands_non_recursive_alias() -> None:
    target = types.UnionType([types.NoneType(), make_any()])
    alias = symbols.TypeAlias('Alias', target)

    assert typeops.get_proper_type(types.TypeAliasType(alias, [])) is target


def test_get_proper_type_rejects_direct_recursive_alias() -> None:
    alias = symbols.TypeAlias('Recur', make_any())
    alias_type = types.TypeAliasType(alias, [])
    alias._target = types.UnionType([types.NoneType(), alias_type])

    with pytest.raises(typeops.RecursiveTypeError):
        typeops.get_proper_type(alias_type)


def test_get_proper_type_rejects_indirect_recursive_alias_cycle() -> None:
    alias_a = symbols.TypeAlias('A', make_any())
    alias_b = symbols.TypeAlias('B', make_any())
    alias_a._target = types.TypeAliasType(alias_b, [])
    alias_b._target = types.UnionType([types.NoneType(), types.TypeAliasType(alias_a, [])])

    with pytest.raises(typeops.RecursiveTypeError):
        typeops.get_proper_type(types.TypeAliasType(alias_a, []))


def test_flatten_nested_unions_rejects_recursive_aliases_by_default() -> None:
    alias = symbols.TypeAlias('Recur', make_any())
    alias_type = types.TypeAliasType(alias, [])
    alias._target = types.UnionType([types.NoneType(), alias_type])

    with pytest.raises(typeops.RecursiveTypeError):
        typeops.flatten_nested_unions([alias_type])


def test_union_type_constructor_flattens_direct_nested_unions() -> None:
    left = types.NoneType()
    middle = make_any()
    right = types.Instance(symbols.TypeInfo('Box'), [])

    union = types.UnionType([left, types.UnionType([middle, right])])

    assert union.items == (left, middle, right)


def test_union_type_constructor_preserves_alias_items() -> None:
    target = types.UnionType([types.NoneType(), make_any()])
    alias = symbols.TypeAlias('Alias', target)
    alias_type = types.TypeAliasType(alias, [])

    union = types.UnionType([alias_type])

    assert union.items == (alias_type,)


def test_make_union_with_no_items_returns_uninhabited() -> None:
    typ = typeops.make_union([])

    assert isinstance(typ, types.UninhabitedType)


def make_literal(value: types.LiteralValue, fullname: str) -> types.LiteralType:
    return types.LiteralType(value, types.Instance(symbols.TypeInfo(fullname, fullname), []))


def test_get_literal_values_returns_single_literal_value() -> None:
    assert typeops.get_literal_values(make_literal('x', 'builtins.str')) == ['x']


def test_get_literal_values_returns_union_literal_values_in_order() -> None:
    typ = types.UnionType([
        make_literal('x', 'builtins.str'),
        make_literal(1, 'builtins.int'),
        make_literal(False, 'builtins.bool'),
    ])

    assert typeops.get_literal_values(typ) == ['x', 1, False]


def test_get_literal_values_or_none_returns_none_for_mixed_union() -> None:
    typ = types.UnionType([
        make_literal('x', 'builtins.str'),
        types.Instance(symbols.TypeInfo('builtins.str'), []),
    ])

    assert typeops.get_literal_values_or_none(typ) is None


def test_get_literal_values_raises_for_non_literal_type() -> None:
    with pytest.raises(ReflectionError, match='finite literal'):
        typeops.get_literal_values(types.Instance(symbols.TypeInfo('builtins.str'), []))


def test_make_union_does_not_contract_bool_literals() -> None:
    true_type = make_literal(True, 'builtins.bool')
    false_type = make_literal(False, 'builtins.bool')

    typ = typeops.make_union([true_type, false_type])

    assert isinstance(typ, types.UnionType)
    assert typ.items == (true_type, false_type)


def test_try_contracting_literals_in_union_contracts_bool_literals() -> None:
    true_type = make_literal(True, 'builtins.bool')
    false_type = make_literal(False, 'builtins.bool')

    contracted = typeops.try_contracting_literals_in_union([true_type, false_type])

    assert len(contracted) == 1
    assert isinstance(contracted[0], types.Instance)
    assert contracted[0].type.fullname == 'builtins.bool'


def test_try_contracting_literals_in_union_preserves_partial_bool_literal_set() -> None:
    true_type = make_literal(True, 'builtins.bool')
    int_type = types.Instance(symbols.TypeInfo('builtins.int'), [])

    assert typeops.try_contracting_literals_in_union([true_type, int_type]) == [
        true_type,
        int_type,
    ]


def test_make_simplified_union_contracts_bool_literals_by_default() -> None:
    true_type = make_literal(True, 'builtins.bool')
    false_type = make_literal(False, 'builtins.bool')

    typ = typeops.make_simplified_union([true_type, false_type])

    assert isinstance(typ, types.Instance)
    assert typ.type.fullname == 'builtins.bool'


def test_make_simplified_union_can_skip_literal_contraction() -> None:
    true_type = make_literal(True, 'builtins.bool')
    false_type = make_literal(False, 'builtins.bool')

    typ = typeops.make_simplified_union([true_type, false_type], contract_literals=False)

    assert isinstance(typ, types.UnionType)
    assert typ.items == (true_type, false_type)


def test_make_simplified_union_flattens_and_collapses_single_item() -> None:
    item = make_any()
    typ = typeops.make_simplified_union([types.UnionType([item])])

    assert typ is item


def test_make_simplified_union_removes_structural_duplicates() -> None:
    info = symbols.TypeInfo('Box')
    left = types.Instance(info, [make_any()])
    duplicate = types.Instance(info, [make_any()])
    other = types.NoneType()

    typ = typeops.make_simplified_union([left, other, duplicate])

    assert isinstance(typ, types.UnionType)
    assert typ.items == (left, other)


def test_make_union_keeps_structural_duplicates() -> None:
    info = symbols.TypeInfo('Box')
    left = types.Instance(info, [make_any()])
    duplicate = types.Instance(info, [make_any()])

    typ = typeops.make_union([left, duplicate])

    assert isinstance(typ, types.UnionType)
    assert typ.items == (left, duplicate)


def test_make_simplified_union_keeps_non_subtype_redundant_items_for_now() -> None:
    int_type = types.Instance(symbols.TypeInfo('builtins.int'), [])
    object_type = types.Instance(symbols.TypeInfo('builtins.object'), [])

    typ = typeops.make_simplified_union([int_type, object_type])

    assert isinstance(typ, types.UnionType)
    assert typ.items == (int_type, object_type)


def test_make_simplified_union_removes_nominal_subtype_before_supertype() -> None:
    object_info = symbols.TypeInfo('builtins.object')
    int_info = symbols.TypeInfo('builtins.int')
    int_info._mro = (int_info, object_info)
    int_type = types.Instance(int_info, [])
    object_type = types.Instance(object_info, [])

    typ = typeops.make_simplified_union([int_type, object_type])

    assert typ is object_type


def test_make_simplified_union_removes_nominal_subtype_after_supertype() -> None:
    object_info = symbols.TypeInfo('builtins.object')
    int_info = symbols.TypeInfo('builtins.int')
    int_info._mro = (int_info, object_info)
    int_type = types.Instance(int_info, [])
    object_type = types.Instance(object_info, [])

    typ = typeops.make_simplified_union([object_type, int_type])

    assert typ is object_type


def test_make_simplified_union_removes_union_subtype_redundancy() -> None:
    object_info = symbols.TypeInfo('builtins.object')
    int_info = symbols.TypeInfo('builtins.int')
    str_info = symbols.TypeInfo('builtins.str')
    int_info._mro = (int_info, object_info)
    str_info._mro = (str_info, object_info)
    int_type = types.Instance(int_info, [])
    str_type = types.Instance(str_info, [])
    object_type = types.Instance(object_info, [])

    typ = typeops.make_simplified_union([types.UnionType([int_type, str_type]), object_type])

    assert typ is object_type


def test_make_simplified_union_collapses_duplicate_any() -> None:
    any_type = make_any()
    duplicate = make_any()

    typ = typeops.make_simplified_union([any_type, duplicate])

    assert typ is any_type


def test_make_simplified_union_keeps_any_with_other_items() -> None:
    any_type = make_any()
    int_type = types.Instance(symbols.TypeInfo('builtins.int'), [])

    typ = typeops.make_simplified_union([int_type, any_type])

    assert isinstance(typ, types.UnionType)
    assert typ.items == (int_type, any_type)


def test_make_simplified_union_removes_reflected_generic_subclass_before_base() -> None:
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    t_var = ta.TypeVar('T')  # type: ignore

    class Box(ta.Generic[t_var]):  # type: ignore
        pass

    class IntBox(Box[int]):  # type: ignore
        pass

    child = reflector.reflect_type(IntBox)
    int_box = reflector.reflect_type(Box[int])  # type: ignore

    typ = typeops.make_simplified_union([child, int_box])

    assert typ is int_box


def test_make_simplified_union_removes_reflected_generic_subclass_after_base() -> None:
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    t_var = ta.TypeVar('T')  # type: ignore

    class Box(ta.Generic[t_var]):  # type: ignore
        pass

    class IntBox(Box[int]):  # type: ignore
        pass

    child = reflector.reflect_type(IntBox)
    int_box = reflector.reflect_type(Box[int])  # type: ignore

    typ = typeops.make_simplified_union([int_box, child])

    assert typ is int_box


def test_make_simplified_union_keeps_reflected_generic_subclass_with_different_base_arg() -> None:
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    t_var = ta.TypeVar('T')  # type: ignore

    class Box(ta.Generic[t_var]):  # type: ignore
        pass

    class IntBox(Box[int]):  # type: ignore
        pass

    child = reflector.reflect_type(IntBox)
    str_box = reflector.reflect_type(Box[str])  # type: ignore

    typ = typeops.make_simplified_union([child, str_box])

    assert isinstance(typ, types.UnionType)
    assert typ.items == (child, str_box)
