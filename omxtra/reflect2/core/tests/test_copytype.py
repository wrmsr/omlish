from .. import symbols
from .. import types
from ..copytype import copy_type
from ..copytype import copy_types


def make_any() -> types.AnyType:
    return types.AnyType(types.TypeOfAny.EXPLICIT)


def make_info(name: str) -> symbols.TypeInfo:
    return symbols.TypeInfo(name, name)


def make_instance(name: str, args: list[types.Type] | None = None) -> types.Instance:
    return types.Instance(make_info(name), [] if args is None else args)


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


def test_copy_type_preserves_atomic_identity() -> None:
    any_type = make_any()
    none_type = types.NoneType()

    assert copy_type(any_type) is any_type
    assert copy_type(none_type) is none_type


def test_copy_type_rebuilds_composite_type_nodes() -> None:
    info = make_info('Box')
    item = types.Instance(info, [make_type_var()])
    typ = types.UnionType([item, types.NoneType()])

    copied = copy_type(typ)

    assert copied is not typ
    assert str(copied) == str(typ)
    assert isinstance(copied, types.UnionType)
    assert copied.items[0] is not item
    assert isinstance(copied.items[0], types.Instance)
    assert copied.items[0].type is info
    assert copied.items[0].args[0] is item.args[0]


def test_copy_type_rebuilds_alias_type_args_but_shares_alias() -> None:
    t_var = make_type_var()
    alias = symbols.TypeAlias('Alias', make_instance('Target', [t_var]))
    typ = types.TypeAliasType(alias, [types.UnionType([t_var, types.NoneType()])])

    copied = copy_type(typ)

    assert copied is not typ
    assert isinstance(copied, types.TypeAliasType)
    assert copied.alias is alias
    assert copied.args[0] is not typ.args[0]
    assert str(copied) == str(typ)


def test_copy_types_returns_list_of_copies() -> None:
    one = types.UnionType([types.NoneType(), make_any()])
    two = make_instance('Box')

    copied = copy_types([one, two])

    assert isinstance(copied, list)
    assert copied[0] is not one
    assert copied[1] is not two
    assert [str(typ) for typ in copied] == [str(one), str(two)]


def test_copy_type_rebuilds_newer_composite_nodes() -> None:
    t_var = make_type_var()
    fallback = make_instance('function')
    dict_fallback = make_instance('dict')
    typ = types.Overloaded([
        types.CallableType(
            [
                types.Parameters([t_var], [symbols.ArgKind.NAMED_OPT], ['value']),
                types.CallableArgument(types.UnpackType(t_var), 'items'),
            ],
            [symbols.ArgKind.POS, symbols.ArgKind.POS],
            [None, None],
            types.TypedDictType({'x': types.PlaceholderType('Later', [t_var])}, {'x'}, {'x'}, dict_fallback),
            fallback,
            variables=[t_var],
        ),
    ])

    copied = copy_type(typ)

    assert copied is not typ
    assert isinstance(copied, types.Overloaded)
    assert copied.items[0] is not typ.items[0]
    assert isinstance(copied.items[0].arg_types[0], types.Parameters)
    assert copied.items[0].arg_types[0] is not typ.items[0].arg_types[0]
    assert isinstance(copied.items[0].arg_types[1], types.CallableArgument)
    assert copied.items[0].arg_types[1] is not typ.items[0].arg_types[1]
    assert isinstance(copied.items[0].arg_types[1].typ, types.UnpackType)
    assert copied.items[0].arg_types[1].typ is not typ.items[0].arg_types[1].typ  # type: ignore
    assert isinstance(copied.items[0].ret_type, types.TypedDictType)
    assert copied.items[0].ret_type is not typ.items[0].ret_type
    assert copied.items[0].ret_type.readonly_keys == {'x'}
    assert isinstance(copied.items[0].ret_type.items['x'], types.PlaceholderType)
    assert copied.items[0].ret_type.items['x'] is not typ.items[0].ret_type.items['x']  # type: ignore
    assert copied.items[0].variables == typ.items[0].variables
