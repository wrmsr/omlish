from .. import symbols
from .. import types
from ..strconv import type_str


def make_any() -> types.AnyType:
    return types.AnyType(types.TypeOfAny.EXPLICIT)


def make_info(name: str, fullname: str | None = None) -> symbols.TypeInfo:
    return symbols.TypeInfo(name, name if fullname is None else fullname)


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


def test_atomic_type_strings() -> None:
    assert type_str(make_any()) == 'Any'
    assert type_str(types.NoneType()) == 'None'
    assert type_str(types.UninhabitedType()) == 'Never'
    assert type_str(make_type_var()) == 'T'


def test_instance_union_and_alias_strings() -> None:
    typ = make_instance('Box', [make_type_var()])
    alias = symbols.TypeAlias('Alias', typ)

    assert str(typ) == 'Box[T]'
    assert repr(types.UnionType([typ, types.NoneType()])) == 'Union[Box[T], None]'
    assert type_str(types.TypeAliasType(alias, [])) == 'Alias'
    assert type_str(types.TypeAliasType(alias, [make_type_var('U')])) == 'Alias[U]'


def test_callable_and_type_type_strings() -> None:
    fallback = make_instance('function')
    typ = types.CallableType(
        [make_instance('A'), make_instance('B')],
        [symbols.ArgKind.POS, symbols.ArgKind.POS],
        [None, None],
        make_instance('R'),
        fallback,
    )

    assert type_str(typ) == 'def (A, B) -> R'
    assert type_str(types.TypeType(make_type_var())) == 'type[T]'


def test_misc_composite_type_strings() -> None:
    fallback = make_instance('tuple')
    assert type_str(types.TupleType([make_instance('A'), make_instance('B')], fallback)) == 'tuple[A, B]'
    assert type_str(types.RequiredType(make_instance('A'))) == 'Required[A]'
    assert type_str(types.RequiredType(make_instance('A'), required=False)) == 'NotRequired[A]'
    assert type_str(types.ReadOnlyType(make_instance('A'))) == 'ReadOnly[A]'

    td = types.TypedDictType(
        {'x': make_instance('A'), 'y': types.ReadOnlyType(make_instance('B'))},
        {'x'},
        {'y'},
        make_instance('dict'),
    )
    assert type_str(td) == "TypedDict({'x': A, 'y'?=: ReadOnly[B]})"

    assert type_str(types.LiteralType('x', make_instance('str'))) == "Literal['x']"
    assert type_str(types.UnboundType('Missing', [make_any()])) == 'Missing?[Any]'
