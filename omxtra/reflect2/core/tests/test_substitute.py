import pytest

from ...errors import ReflectionError
from .. import symbols
from .. import types
from ..substitute import substitute_type
from ..substitute import substitute_types
from .helpers import make_recursive_mixed_tuple_alias_case
from .helpers import make_recursive_variadic_tuple_alias_case


def make_any() -> types.AnyType:
    return types.AnyType(types.TypeOfAny.EXPLICIT)


def make_info(name: str) -> symbols.TypeInfo:
    return symbols.TypeInfo(name, name)


def make_instance(name: str, args: list[types.Type] | None = None) -> types.Instance:
    return types.Instance(make_info(name), [] if args is None else args)


def make_type_var(name: str, raw_id: int) -> types.TypeVarType:
    any_type = make_any()
    return types.TypeVarType(
        name,
        name,
        types.TypeVarId(raw_id),
        [],
        any_type,
        any_type,
    )


def make_type_var_tuple(name: str, raw_id: int) -> types.TypeVarTupleType:
    any_type = make_any()
    tuple_fallback = make_instance('tuple', [any_type])
    return types.TypeVarTupleType(
        name,
        name,
        types.TypeVarId(raw_id),
        any_type,
        any_type,
        tuple_fallback,
    )


def test_substitute_type_replaces_type_var_by_id() -> None:
    t_var = make_type_var('T', 1)
    typ = make_instance('Box', [t_var])

    substituted = substitute_type(typ, {t_var.id: make_instance('A')})

    assert str(substituted) == 'Box[A]'


def test_substitute_type_replaces_type_var_by_object() -> None:
    t_var = make_type_var('T', 1)
    typ = make_instance('Box', [t_var])

    substituted = substitute_type(typ, {t_var: make_instance('A')})

    assert str(substituted) == 'Box[A]'


def test_substitute_type_preserves_unmapped_type_var() -> None:
    t_var = make_type_var('T', 1)
    typ = make_instance('Box', [t_var])

    substituted = substitute_type(typ, {})

    assert str(substituted) == 'Box[T]'


def test_substitute_type_rewrites_callable_arguments_and_return() -> None:
    t_var = make_type_var('T', 1)
    typ = types.CallableType(
        [t_var],
        [symbols.ArgKind.POS],
        [None],
        t_var,
        make_instance('function'),
    )

    substituted = substitute_type(typ, {t_var.id: make_instance('A')})

    assert isinstance(substituted, types.CallableType)
    assert str(substituted) == 'def (A) -> A'


def test_substitute_types_reuses_replacements_across_list() -> None:
    t_var = make_type_var('T', 1)

    substituted = substitute_types(
        [
            make_instance('Box', [t_var]),
            make_instance('Holder', [t_var]),
        ],
        {t_var.id: make_instance('A')},
    )

    assert [str(typ) for typ in substituted] == ['Box[A]', 'Holder[A]']


def test_substitute_type_rewrites_newer_composite_nodes() -> None:
    t_var = make_type_var('T', 1)
    replacement = make_instance('A')
    fallback = make_instance('function')
    dict_fallback = make_instance('dict')
    typ = types.Overloaded([
        types.CallableType(
            [types.CallableArgument(t_var, 'value')],
            [symbols.ArgKind.POS],
            [None],
            types.TypedDictType({'x': t_var}, {'x'}, {'x'}, dict_fallback),
            fallback,
            variables=[t_var],
        ),
        types.CallableType(
            [types.TypeList([t_var]), types.UnpackType(t_var)],
            [symbols.ArgKind.POS, symbols.ArgKind.POS],
            [None, None],
            types.PlaceholderType('Later', [t_var]),
            fallback,
        ),
    ])

    substituted = substitute_type(typ, {t_var: replacement})

    assert isinstance(substituted, types.Overloaded)
    assert isinstance(substituted.items[0].arg_types[0], types.CallableArgument)
    assert str(substituted.items[0].arg_types[0].typ) == 'A'
    assert isinstance(substituted.items[0].ret_type, types.TypedDictType)
    assert str(substituted.items[0].ret_type.items['x']) == 'A'
    assert substituted.items[0].ret_type.readonly_keys == {'x'}
    assert isinstance(substituted.items[1].arg_types[0], types.TypeList)
    assert str(substituted.items[1].arg_types[0].items[0]) == 'A'
    assert str(substituted.items[1].arg_types[1]) == 'Unpack[A]'
    assert str(substituted.items[1].ret_type) == '<placeholder Later[A]>'


def test_substitute_type_splices_type_var_tuple_inside_tuple() -> None:
    type_var_tuple = make_type_var_tuple('Ts', 1)
    int_type = make_instance('int')
    str_type = make_instance('str')
    bool_type = make_instance('bool')
    tuple_fallback = make_instance('tuple', [make_any()])
    typ = types.TupleType([int_type, types.UnpackType(type_var_tuple), bool_type], tuple_fallback)
    replacement = types.TupleType([str_type], tuple_fallback)

    substituted = substitute_type(typ, {type_var_tuple: replacement})

    assert isinstance(substituted, types.TupleType)
    assert [str(item) for item in substituted.items] == ['int', 'str', 'bool']


def test_substitute_type_splices_type_list_for_bare_type_var_tuple_inside_tuple() -> None:
    type_var_tuple = make_type_var_tuple('Ts', 1)
    int_type = make_instance('int')
    str_type = make_instance('str')
    tuple_fallback = make_instance('tuple', [make_any()])
    typ = types.TupleType([int_type, type_var_tuple], tuple_fallback)
    replacement = types.TypeList([str_type])

    substituted = substitute_type(typ, {type_var_tuple.id: replacement})

    assert isinstance(substituted, types.TupleType)
    assert [str(item) for item in substituted.items] == ['int', 'str']


def test_substitute_type_keeps_ordinary_type_var_tuple_replacement_nested() -> None:
    t_var = make_type_var('T', 1)
    int_type = make_instance('int')
    str_type = make_instance('str')
    tuple_fallback = make_instance('tuple', [make_any()])
    typ = types.TupleType([t_var], tuple_fallback)
    replacement = types.TupleType([int_type, str_type], tuple_fallback)

    substituted = substitute_type(typ, {t_var: replacement})

    assert isinstance(substituted, types.TupleType)
    assert list(substituted.items) == [replacement]


def test_substitute_type_rewrites_recursive_variadic_alias_args() -> None:
    case = make_recursive_variadic_tuple_alias_case('TupleNode', 1)

    substituted = substitute_type(case.alias_type, {case.type_var_tuple: case.packed_concrete_arg})

    assert isinstance(substituted, types.TypeAliasType)
    assert substituted.alias is case.alias
    assert [str(arg) for arg in substituted.args] == ['tuple[builtins.int, builtins.str]']
    assert str(case.alias.target) == 'tuple[Unpack[TupleNodeTs], TupleNode[tuple[Unpack[TupleNodeTs]]]]'


def test_substitute_type_splices_recursive_variadic_alias_target() -> None:
    case = make_recursive_variadic_tuple_alias_case('TupleNode', 1)

    substituted = substitute_type(case.alias.target, {case.type_var_tuple: case.packed_concrete_arg})

    assert isinstance(substituted, types.TupleType)
    assert [str(item) for item in substituted.items] == [
        'builtins.int',
        'builtins.str',
        'TupleNode[tuple[builtins.int, builtins.str]]',
    ]


def test_substitute_type_rewrites_recursive_mixed_alias_args() -> None:
    case = make_recursive_mixed_tuple_alias_case('MixedNode', 1, 2)

    substituted = substitute_type(
        case.alias_type,
        {
            case.type_var: case.concrete_type_var_item,
            case.type_var_tuple: case.packed_concrete_arg,
        },
    )

    assert isinstance(substituted, types.TypeAliasType)
    assert substituted.alias is case.alias
    assert [str(arg) for arg in substituted.args] == [
        'builtins.str',
        'tuple[builtins.int, builtins.bool]',
    ]


def test_substitute_type_splices_recursive_mixed_alias_target() -> None:
    case = make_recursive_mixed_tuple_alias_case('MixedNode', 1, 2)

    substituted = substitute_type(
        case.alias.target,
        {
            case.type_var: case.concrete_type_var_item,
            case.type_var_tuple: case.packed_concrete_arg,
        },
    )

    assert isinstance(substituted, types.TupleType)
    assert [str(item) for item in substituted.items] == [
        'builtins.str',
        'builtins.int',
        'builtins.bool',
        'MixedNode[builtins.str, tuple[builtins.int, builtins.bool]]',
    ]


def test_substitute_type_rejects_unsupported_key() -> None:
    with pytest.raises(ReflectionError):
        substitute_type(make_instance('Box'), {'T': make_instance('A')})


def test_substitute_type_rejects_unsupported_value() -> None:
    t_var = make_type_var('T', 1)

    with pytest.raises(ReflectionError):
        substitute_type(make_instance('Box', [t_var]), {t_var.id: object()})
