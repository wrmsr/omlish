from .. import symbols
from .. import types
from ..expandtype import expand_type
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


def test_expand_type_replaces_type_var_by_id() -> None:
    t_var = make_type_var('T', 1)
    typ = make_instance('Box', [t_var])

    expanded = expand_type(typ, {t_var.id: make_instance('A')})

    assert str(expanded) == 'Box[A]'


def test_expand_type_replaces_type_var_by_object() -> None:
    t_var = make_type_var('T', 1)
    typ = make_instance('Box', [t_var])

    expanded = expand_type(typ, {t_var: make_instance('A')})

    assert str(expanded) == 'Box[A]'


def test_expand_type_preserves_unmapped_type_var() -> None:
    t_var = make_type_var('T', 1)
    typ = make_instance('Box', [t_var])

    expanded = expand_type(typ, {})

    assert str(expanded) == 'Box[T]'


def test_expand_type_rewrites_callable_arguments_and_return() -> None:
    t_var = make_type_var('T', 1)
    typ = types.CallableType(
        [t_var],
        [symbols.ArgKind.POS],
        [None],
        t_var,
        make_instance('function'),
    )

    expanded = expand_type(typ, {t_var.id: make_instance('A')})

    assert isinstance(expanded, types.CallableType)
    assert str(expanded) == 'def (A) -> A'


def test_expand_type_rewrites_alias_args_but_not_alias_target() -> None:
    t_var = make_type_var('T', 1)
    alias = symbols.TypeAlias('Alias', make_instance('Target', [t_var]))
    typ = types.TypeAliasType(alias, [t_var])

    expanded = expand_type(typ, {t_var.id: make_instance('A')})

    assert str(expanded) == 'Alias[A]'
    assert alias.target is not expanded
    assert str(alias.target) == 'Target[T]'


def test_expand_type_rewrites_recursive_variadic_alias_args() -> None:
    case = make_recursive_variadic_tuple_alias_case('TupleNode', 1)

    expanded = expand_type(case.alias_type, {case.type_var_tuple: case.packed_concrete_arg})

    assert isinstance(expanded, types.TypeAliasType)
    assert expanded.alias is case.alias
    assert [str(arg) for arg in expanded.args] == ['tuple[builtins.int, builtins.str]']
    assert str(case.alias.target) == 'tuple[Unpack[TupleNodeTs], TupleNode[tuple[Unpack[TupleNodeTs]]]]'


def test_expand_type_splices_recursive_variadic_alias_target() -> None:
    case = make_recursive_variadic_tuple_alias_case('TupleNode', 1)

    expanded = expand_type(case.alias.target, {case.type_var_tuple: case.packed_concrete_arg})

    assert isinstance(expanded, types.TupleType)
    assert [str(item) for item in expanded.items] == [
        'builtins.int',
        'builtins.str',
        'TupleNode[tuple[builtins.int, builtins.str]]',
    ]


def test_expand_type_rewrites_newer_composite_nodes() -> None:
    t_var = make_type_var('T', 1)
    replacement = make_instance('A')
    fallback = make_instance('function')
    dict_fallback = make_instance('dict')
    typ = types.Overloaded([
        types.CallableType(
            [types.UnpackType(t_var)],
            [symbols.ArgKind.POS],
            [None],
            types.TypedDictType({'x': t_var}, {'x'}, set(), dict_fallback),
            fallback,
            variables=[t_var],
        ),
        types.CallableType(
            [types.Parameters([t_var], [symbols.ArgKind.NAMED_OPT], ['value'])],
            [symbols.ArgKind.POS],
            [None],
            types.PlaceholderType('Later', [t_var]),
            fallback,
        ),
    ])

    expanded = expand_type(typ, {t_var.id: replacement})

    assert isinstance(expanded, types.Overloaded)
    assert str(expanded.items[0].arg_types[0]) == 'Unpack[A]'
    assert isinstance(expanded.items[0].ret_type, types.TypedDictType)
    assert str(expanded.items[0].ret_type.items['x']) == 'A'
    assert expanded.items[0].variables == (t_var,)
    assert isinstance(expanded.items[1].arg_types[0], types.Parameters)
    assert str(expanded.items[1].arg_types[0].arg_types[0]) == 'A'
    assert expanded.items[1].arg_types[0].arg_kinds == (symbols.ArgKind.NAMED_OPT,)
    assert expanded.items[1].arg_types[0].arg_names == ('value',)
    assert str(expanded.items[1].ret_type) == '<placeholder Later[A]>'


def test_expand_type_overload_allows_alias_replacements_inside_callable_items() -> None:
    t_var = make_type_var('T', 1)
    fallback = make_instance('function')
    alias = symbols.TypeAlias('Alias', make_any())
    typ = types.Overloaded([
        types.CallableType([t_var], [symbols.ArgKind.POS], [None], t_var, fallback),
    ])

    expanded = expand_type(typ, {t_var.id: types.TypeAliasType(alias, [])})

    assert isinstance(expanded, types.Overloaded)
    assert isinstance(expanded.items[0].arg_types[0], types.TypeAliasType)
    assert isinstance(expanded.items[0].ret_type, types.TypeAliasType)
    assert expanded.items[0].arg_types[0].alias is alias
    assert expanded.items[0].ret_type.alias is alias


def test_expand_type_allows_bare_type_var_alias_replacement() -> None:
    t_var = make_type_var('T', 1)
    alias = types.TypeAliasType(symbols.TypeAlias('Alias', make_any()), [])

    expanded = expand_type(t_var, {t_var.id: alias})

    assert expanded is alias
