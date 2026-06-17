# ruff: noqa: PLC0132 SLF001
import typing as ta

import pytest

from ...errors import ReflectionError
from ...errors import UnsupportedTypeOperationError
from ...reflect import TypeReflector
from ...universe import TypeUniverse
from .. import symbols
from .. import types
from ..join import join_type_list
from ..join import join_types
from ..join import structural_join_type_list
from ..join import structural_join_types
from ..strconv import type_str
from .helpers import make_any
from .helpers import make_info
from .helpers import make_instance
from .helpers import make_recursive_json_like_alias_case
from .helpers import make_recursive_variadic_tuple_alias_case
from .helpers import make_type_var
from .helpers import make_type_var_tuple
from .helpers import make_typed_dict


def test_join_same_type_returns_left() -> None:
    info = make_info('Thing')
    left = make_instance(info)
    right = make_instance(info)

    assert join_types(left, right) is left


def test_join_any_returns_any() -> None:
    any_type = make_any()
    int_type = make_instance(make_info('int'))

    assert join_types(any_type, int_type) is any_type
    assert join_types(int_type, any_type) is any_type


def test_join_nominal_subtype_returns_supertype() -> None:
    base_info = make_info('Base')
    child_info = make_info('Child')
    child_info._mro = (child_info, base_info)
    child = make_instance(child_info)
    base = make_instance(base_info)

    assert join_types(child, base) is base
    assert join_types(base, child) is base


def test_join_reflected_generic_subclass_returns_matching_base() -> None:
    reflector = TypeReflector(TypeUniverse())
    t_var = ta.TypeVar('T')  # type: ignore

    class Box(ta.Generic[t_var]):  # type: ignore
        pass

    class IntBox(Box[int]):  # type: ignore
        pass

    child = reflector.reflect_type(IntBox)
    int_box = reflector.reflect_type(Box[int])  # type: ignore

    assert join_types(child, int_box) is int_box
    assert join_types(int_box, child) is int_box


def test_join_reflected_generic_subclass_with_different_base_arg_returns_union() -> None:
    reflector = TypeReflector(TypeUniverse())
    t_var = ta.TypeVar('T')  # type: ignore

    class Box(ta.Generic[t_var]):  # type: ignore
        pass

    class IntBox(Box[int]):  # type: ignore
        pass

    child = reflector.reflect_type(IntBox)
    str_box = reflector.reflect_type(Box[str])  # type: ignore

    typ = join_types(child, str_box)

    assert isinstance(typ, types.UnionType)
    assert typ.items == (child, str_box)


def test_join_unrelated_supported_instances_returns_union() -> None:
    left = make_instance(make_info('Left'))
    right = make_instance(make_info('Right'))

    typ = join_types(left, right)

    assert isinstance(typ, types.UnionType)
    assert typ.items == (left, right)


def test_join_union_flattens_and_simplifies_items() -> None:
    base_info = make_info('Base')
    child_info = make_info('Child')
    other_info = make_info('Other')
    child_info._mro = (child_info, base_info)
    child = make_instance(child_info)
    base = make_instance(base_info)
    other = make_instance(other_info)

    typ = join_types(types.UnionType([child, other]), base)

    assert isinstance(typ, types.UnionType)
    assert typ.items == (other, base)


def test_join_union_with_union_flattens_and_simplifies_items() -> None:
    base_info = make_info('Base')
    child_info = make_info('Child')
    left_info = make_info('Left')
    right_info = make_info('Right')
    child_info._mro = (child_info, base_info)
    child = make_instance(child_info)
    base = make_instance(base_info)
    left = make_instance(left_info)
    right = make_instance(right_info)

    typ = join_types(types.UnionType([left, child]), types.UnionType([base, right]))

    assert isinstance(typ, types.UnionType)
    assert typ.items == (left, base, right)


def test_join_typed_dict_subtype_returns_wider_type() -> None:
    int_type = make_instance(make_info('int'))
    source = make_typed_dict({'x': int_type, 'extra': int_type}, {'x', 'extra'})
    target = make_typed_dict({'x': int_type}, {'x'})

    assert join_types(source, target) is target


def test_join_typed_dicts_keeps_shared_compatible_keys() -> None:
    int_type = make_instance(make_info('int'))
    left = make_typed_dict({'x': int_type, 'left': int_type}, {'x', 'left'})
    right = make_typed_dict({'x': int_type, 'right': int_type}, {'x', 'right'})

    typ = join_types(left, right)

    assert isinstance(typ, types.TypedDictType)
    assert type_str(typ) == "TypedDict({'x': int})"


def test_join_typed_dicts_drops_incompatible_mutable_keys() -> None:
    left = make_typed_dict({'x': make_instance(make_info('int'))}, {'x'})
    right = make_typed_dict({'x': make_instance(make_info('str'))}, {'x'})

    typ = join_types(left, right)

    assert isinstance(typ, types.TypedDictType)
    assert type_str(typ) == 'TypedDict({})'


def test_join_typed_dicts_joins_readonly_key_covariantly() -> None:
    base_info = make_info('Base')
    child_info = make_info('Child')
    child_info._mro = (child_info, base_info)
    left = make_typed_dict({'x': make_instance(child_info)}, {'x'}, {'x'})
    right = make_typed_dict({'x': make_instance(base_info)}, {'x'}, {'x'})

    typ = join_types(left, right)

    assert isinstance(typ, types.TypedDictType)
    assert type_str(typ) == "TypedDict({'x'=: Base})"


def test_join_raises_for_unsupported_subtype_relation() -> None:
    fallback = make_instance(make_info('function'))
    callable_type = types.CallableType([], [], [], make_any(), fallback)

    with pytest.raises(UnsupportedTypeOperationError):
        join_types(callable_type, make_instance(make_info('object')))


def test_join_strips_type_guarded_and_annotated_wrappers() -> None:
    base_info = make_info('Base')
    child_info = make_info('Child')
    child_info._mro = (child_info, base_info)
    child = make_instance(child_info)
    base = make_instance(base_info)

    assert join_types(types.TypeGuardedType(child), base) is base
    assert join_types(types.AnnotatedType(child, ('cfg',)), base) is base
    assert join_types(child, types.AnnotatedType(base, ('cfg',))) is base


def test_join_required_readonly_unpack_and_type_type_fail_closed_for_now() -> None:
    item = make_instance(make_info('Item'))
    target = make_instance(make_info('Target'))
    cases = [
        types.RequiredType(item),
        types.ReadOnlyType(item),
        types.UnpackType(item),
    ]

    for typ in cases:
        with pytest.raises(UnsupportedTypeOperationError, match='Unsupported join'):
            join_types(typ, target)


def test_join_type_type_returns_wider_class_object_type() -> None:
    base_info = make_info('Base')
    child_info = make_info('Child')
    child_info._mro = (child_info, base_info)
    child_type = types.TypeType(make_instance(child_info))
    base_type = types.TypeType(make_instance(base_info))

    assert type_str(join_types(child_type, base_type)) == 'type[Base]'
    assert type_str(join_types(base_type, child_type)) == 'type[Base]'


def test_join_type_type_with_unsupported_item_relation_fails_closed() -> None:
    fallback = make_instance(make_info('function'))
    callable_type = types.CallableType([], [], [], make_any(), fallback)
    item = make_instance(make_info('Item'))

    with pytest.raises(UnsupportedTypeOperationError, match='Unsupported join'):
        join_types(types.TypeType(callable_type), types.TypeType(item))


def test_join_unrelated_type_types_returns_class_object_union() -> None:
    left = types.TypeType(make_instance(make_info('Left')))
    right = types.TypeType(make_instance(make_info('Right')))

    typ = join_types(left, right)

    assert type_str(typ) == 'type[Union[Left, Right]]'


def test_join_union_of_type_types_simplifies_redundant_subtype_item() -> None:
    base_info = make_info('Base')
    child_info = make_info('Child')
    other_info = make_info('Other')
    child_info._mro = (child_info, base_info)
    child_type = types.TypeType(make_instance(child_info))
    base_type = types.TypeType(make_instance(base_info))
    other_type = types.TypeType(make_instance(other_info))

    typ = join_types(types.UnionType([child_type, other_type]), base_type)

    assert isinstance(typ, types.UnionType)
    assert [type_str(item) for item in typ.items] == ['type[Other]', 'type[Base]']


def test_join_fixed_tuples_synthesizes_itemwise_join() -> None:
    object_info = make_info('builtins.object')
    int_info = make_info('builtins.int')
    str_info = make_info('builtins.str')
    int_info._mro = (int_info, object_info)
    str_info._mro = (str_info, object_info)
    fallback = make_instance(make_info('builtins.tuple'), [make_any()])

    left = types.TupleType([make_instance(int_info), make_instance(object_info)], fallback)
    right = types.TupleType([make_instance(object_info), make_instance(str_info)], fallback)
    typ = join_types(left, right)

    assert isinstance(typ, types.TupleType)
    assert type_str(typ) == 'tuple[builtins.object, builtins.object]'


def test_join_fixed_tuples_with_different_lengths_returns_union() -> None:
    fallback = make_instance(make_info('builtins.tuple'), [make_any()])
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))

    left = types.TupleType([int_type], fallback)
    right = types.TupleType([int_type, str_type], fallback)
    typ = join_types(left, right)

    assert isinstance(typ, types.UnionType)
    assert typ.items == (left, right)


def test_structural_join_expands_variadic_alias_to_fixed_tuple() -> None:
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

    assert structural_join_types(alias_type, target) is alias_type
    assert structural_join_types(target, alias_type) is target


def test_join_fails_closed_for_variadic_tuple_shapes() -> None:
    fallback = make_instance(make_info('builtins.tuple'), [make_any()])
    int_type = make_instance(make_info('builtins.int'))
    type_var_tuple = make_type_var_tuple('Ts', 1)
    variadic = types.TupleType([types.UnpackType(type_var_tuple)], fallback)
    concrete = types.TupleType([int_type], fallback)

    with pytest.raises(UnsupportedTypeOperationError, match='variadic Tuple join'):
        join_types(variadic, concrete)

    with pytest.raises(UnsupportedTypeOperationError, match='variadic Tuple join'):
        structural_join_types(concrete, variadic)


def test_join_simple_callables_returns_more_general_callable() -> None:
    base_info = make_info('Base')
    child_info = make_info('Child')
    child_info._mro = (child_info, base_info)
    base = make_instance(base_info)
    child = make_instance(child_info)
    fallback = make_instance(make_info('function'))

    left = types.CallableType([base], [symbols.ArgKind.POS], [None], child, fallback)
    right = types.CallableType([child], [symbols.ArgKind.POS], [None], base, fallback)

    assert join_types(left, right) is right
    assert join_types(right, left) is right


def test_join_same_shape_callables_synthesizes_contravariant_args_and_covariant_return() -> None:
    base_info = make_info('Base')
    child_info = make_info('Child')
    child_info._mro = (child_info, base_info)
    base = make_instance(base_info)
    child = make_instance(child_info)
    fallback = make_instance(make_info('function'))

    left = types.CallableType([base], [symbols.ArgKind.POS], [None], base, fallback)
    right = types.CallableType([child], [symbols.ArgKind.POS], [None], child, fallback)

    typ = join_types(left, right)

    assert isinstance(typ, types.CallableType)
    assert type_str(typ) == 'def (Child) -> Base'


def test_join_same_shape_callables_preserves_keyword_only_shape() -> None:
    base_info = make_info('Base')
    child_info = make_info('Child')
    child_info._mro = (child_info, base_info)
    base = make_instance(base_info)
    child = make_instance(child_info)
    fallback = make_instance(make_info('function'))

    left = types.CallableType([base], [symbols.ArgKind.NAMED_OPT], ['value'], base, fallback)
    right = types.CallableType([child], [symbols.ArgKind.NAMED_OPT], ['value'], child, fallback)

    typ = join_types(left, right)

    assert isinstance(typ, types.CallableType)
    assert typ.arg_kinds == (symbols.ArgKind.NAMED_OPT,)
    assert typ.arg_names == ('value',)
    assert type_str(typ) == 'def (Child) -> Base'


def test_join_callables_with_incompatible_shape_returns_union() -> None:
    item = make_instance(make_info('Item'))
    ret = make_instance(make_info('Ret'))
    fallback = make_instance(make_info('function'))

    left = types.CallableType([item], [symbols.ArgKind.POS], [None], ret, fallback)
    right = types.CallableType([item], [symbols.ArgKind.NAMED], ['value'], ret, fallback)

    joined = join_types(left, right)

    assert isinstance(joined, types.UnionType)
    assert joined.items == (left, right)


def test_join_same_shape_callables_with_different_fallbacks_fails_closed() -> None:
    base_info = make_info('Base')
    child_info = make_info('Child')
    child_info._mro = (child_info, base_info)
    base = make_instance(base_info)
    child = make_instance(child_info)
    left = types.CallableType(
        [base],
        [symbols.ArgKind.POS],
        [None],
        base,
        make_instance(make_info('function')),
    )
    right = types.CallableType(
        [child],
        [symbols.ArgKind.POS],
        [None],
        child,
        make_instance(make_info('other_function')),
    )

    with pytest.raises(UnsupportedTypeOperationError, match='different fallbacks'):
        join_types(left, right)


def test_join_generic_callable_fails_closed_for_now() -> None:
    fallback = make_instance(make_info('function'))
    t_var = make_type_var('T', 1)
    other = make_instance(make_info('Other'))
    left = types.CallableType([t_var], [symbols.ArgKind.POS], [None], t_var, fallback, variables=[t_var])
    right = types.CallableType([t_var], [symbols.ArgKind.POS], [None], other, fallback)

    with pytest.raises(UnsupportedTypeOperationError, match='Unsupported join'):
        join_types(left, right)


def test_join_same_overload_returns_left() -> None:
    fallback = make_instance(make_info('function'))
    int_type = make_instance(make_info('int'))
    str_type = make_instance(make_info('str'))
    left = types.Overloaded([
        types.CallableType([int_type], [], [], int_type, fallback),
        types.CallableType([str_type], [], [], str_type, fallback),
    ])
    right = types.Overloaded(list(left.items))

    assert join_types(left, right) is left


def test_join_different_overload_synthesizes_pairwise_items() -> None:
    fallback = make_instance(make_info('function'))
    int_type = make_instance(make_info('int'))
    str_type = make_instance(make_info('str'))
    left = types.Overloaded([
        types.CallableType([int_type], [], [], int_type, fallback),
        types.CallableType([str_type], [], [], str_type, fallback),
    ])
    right = types.Overloaded([
        types.CallableType([str_type], [], [], str_type, fallback),
        types.CallableType([int_type], [], [], int_type, fallback),
    ])

    typ = join_types(left, right)

    assert isinstance(typ, types.Overloaded)
    assert type_str(typ) == 'Overload(def (Never) -> Union[int, str], def (Never) -> Union[str, int])'


def test_join_overload_and_callable_fails_closed_for_now() -> None:
    fallback = make_instance(make_info('function'))
    int_type = make_instance(make_info('int'))
    callable_type = types.CallableType([int_type], [], [], int_type, fallback)
    overloaded = types.Overloaded([callable_type])

    with pytest.raises(UnsupportedTypeOperationError, match='Unsupported join'):
        join_types(overloaded, callable_type)


def test_join_type_list_empty_returns_uninhabited() -> None:
    typ = join_type_list([])

    assert isinstance(typ, types.UninhabitedType)


def test_join_type_list_singleton_returns_item() -> None:
    item = make_instance(make_info('Item'))

    assert join_type_list([item]) is item


def test_join_type_list_folds_multiple_items() -> None:
    base_info = make_info('Base')
    child_info = make_info('Child')
    other_info = make_info('Other')
    child_info._mro = (child_info, base_info)
    child = make_instance(child_info)
    base = make_instance(base_info)
    other = make_instance(other_info)

    typ = join_type_list([child, other, base])

    assert isinstance(typ, types.UnionType)
    assert typ.items == (other, base)


def test_structural_join_literal_alias_with_fallback_returns_fallback() -> None:
    str_type = make_instance(make_info('builtins.str'))
    literal = types.LiteralType('debug', str_type)
    alias = symbols.TypeAlias('Mode', literal)
    alias_type = types.TypeAliasType(alias, [])

    assert structural_join_types(alias_type, str_type) is str_type
    assert structural_join_types(types.AnnotatedType(alias_type, ('cfg',)), str_type) is str_type


def test_structural_join_preserves_newtype_identity_through_aliases() -> None:
    int_type = make_instance(make_info('builtins.int'))
    user_info = make_info('example.UserId')
    account_info = make_info('example.AccountId')
    user_info._new_type_supertype = int_type
    account_info._new_type_supertype = int_type
    user_id = make_instance(user_info)
    account_id = make_instance(account_info)
    user_alias = symbols.TypeAlias('UserAlias', user_id)
    account_alias = symbols.TypeAlias('AccountAlias', account_id)
    user_alias_type = types.TypeAliasType(user_alias, [])
    account_alias_type = types.TypeAliasType(account_alias, [])

    assert structural_join_types(user_alias_type, user_id) is user_alias_type

    typ = structural_join_types(user_alias_type, account_alias_type)

    assert isinstance(typ, types.UnionType)
    assert typ.items == (user_alias_type, account_alias_type)


def test_structural_join_recursive_alias_matches_one_unrolling() -> None:
    list_info = make_info('builtins.list')
    int_type = make_instance(make_info('builtins.int'))
    alias = symbols.TypeAlias('Node', make_any())
    alias_type = types.TypeAliasType(alias, [])
    alias._target = types.UnionType([int_type, make_instance(list_info, [alias_type])])

    assert structural_join_types(alias_type, alias.target) is alias_type
    with pytest.raises(ReflectionError):
        join_types(alias_type, alias.target)


def test_structural_join_recursive_alias_with_object_bound_returns_object() -> None:
    object_info = make_info('builtins.object')
    int_info = make_info('builtins.int')
    list_info = make_info('builtins.list')
    int_info._mro = (int_info, object_info)
    list_info._mro = (list_info, object_info)
    object_type = make_instance(object_info)
    alias = symbols.TypeAlias('Node', make_any())
    alias_type = types.TypeAliasType(alias, [])
    alias._target = types.UnionType([make_instance(int_info), make_instance(list_info, [alias_type])])

    assert structural_join_types(alias_type, object_type) is object_type
    assert structural_join_types(object_type, alias_type) is object_type


def test_structural_join_json_like_recursive_alias_matches_one_unrolling_and_equivalent_alias() -> None:
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

    assert structural_join_types(left.alias_type, left.one_unrolling) is left.alias_type
    assert structural_join_types(left.one_unrolling, left.alias_type) is left.one_unrolling
    assert structural_join_types(left.alias_type, right.alias_type) is left.alias_type
    assert structural_join_type_list([left.alias_type, left.one_unrolling, right.alias_type]) is left.alias_type


def test_structural_join_recursive_variadic_tuple_alias_matches_one_unrolling() -> None:
    case = make_recursive_variadic_tuple_alias_case('TupleNode', 1)

    assert structural_join_types(case.concrete_alias_type, case.one_unrolling) is case.concrete_alias_type
    assert structural_join_type_list([case.concrete_alias_type, case.one_unrolling]) is case.concrete_alias_type


def test_structural_join_recursive_aliases_with_different_identity_same_structure() -> None:
    list_info = make_info('builtins.list')
    int_type = make_instance(make_info('builtins.int'))
    left_alias = symbols.TypeAlias('Left', make_any())
    right_alias = symbols.TypeAlias('Right', make_any())
    left_alias_type = types.TypeAliasType(left_alias, [])
    right_alias_type = types.TypeAliasType(right_alias, [])
    left_alias._target = types.UnionType([int_type, make_instance(list_info, [left_alias_type])])
    right_alias._target = types.UnionType([int_type, make_instance(list_info, [right_alias_type])])

    assert structural_join_types(left_alias_type, right_alias_type) is left_alias_type


def test_structural_join_incompatible_recursive_aliases_returns_union() -> None:
    list_info = make_info('builtins.list')
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))
    left_alias = symbols.TypeAlias('Left', make_any())
    right_alias = symbols.TypeAlias('Right', make_any())
    left_alias_type = types.TypeAliasType(left_alias, [])
    right_alias_type = types.TypeAliasType(right_alias, [])
    left_alias._target = types.UnionType([int_type, make_instance(list_info, [left_alias_type])])
    right_alias._target = types.UnionType([str_type, make_instance(list_info, [right_alias_type])])

    typ = structural_join_types(left_alias_type, right_alias_type)

    assert isinstance(typ, types.UnionType)
    assert typ.items == (left_alias_type, right_alias_type)


def test_structural_join_recursive_alias_with_unsupported_callable_target_fails_closed() -> None:
    fallback = make_instance(make_info('function'))
    t_var = make_type_var('T', 1)
    other = make_instance(make_info('Other'))
    alias = symbols.TypeAlias('Fn', make_any())
    alias_type = types.TypeAliasType(alias, [])
    alias._target = types.CallableType([t_var], [symbols.ArgKind.POS], [None], alias_type, fallback, variables=[t_var])
    target = types.CallableType([other], [symbols.ArgKind.POS], [None], other, fallback)

    with pytest.raises(UnsupportedTypeOperationError):
        structural_join_types(alias_type, target)


def test_structural_join_type_list_folds_recursive_aliases() -> None:
    list_info = make_info('builtins.list')
    int_type = make_instance(make_info('builtins.int'))
    alias = symbols.TypeAlias('Node', make_any())
    alias_type = types.TypeAliasType(alias, [])
    alias._target = types.UnionType([int_type, make_instance(list_info, [alias_type])])

    assert structural_join_type_list([alias_type, alias.target]) is alias_type
