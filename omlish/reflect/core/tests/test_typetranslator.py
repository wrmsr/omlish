from .. import symbols
from .. import types
from ..typevisitor import TypeTranslator


class NoneToAnyTranslator(TypeTranslator):
    def visit_none_type(self, typ: types.NoneType) -> types.Type:
        return types.AnyType(types.TypeOfAny.EXPLICIT)


def make_info(name: str) -> symbols.TypeInfo:
    return symbols.TypeInfo(name, name)


def make_instance(name: str, args: list[types.Type] | None = None) -> types.Instance:
    return types.Instance(make_info(name), [] if args is None else args)


def test_identity_translator_preserves_atomic_nodes() -> None:
    typ = types.AnyType(types.TypeOfAny.EXPLICIT)

    assert typ.accept(TypeTranslator()) is typ


def test_type_translator_rewrites_nested_instance_args() -> None:
    typ = types.Instance(make_info('Box'), [types.NoneType()])

    translated = typ.accept(NoneToAnyTranslator())

    assert isinstance(translated, types.Instance)
    assert translated is not typ
    assert isinstance(translated.args[0], types.AnyType)


def test_type_translator_rewrites_union_and_wrappers() -> None:
    alias = symbols.TypeAlias('Alias', make_instance('Target'))
    typ = types.UnionType([
        types.RequiredType(types.NoneType()),
        types.TypeAliasType(alias, [types.NoneType()]),
    ])

    translated = typ.accept(NoneToAnyTranslator())

    assert str(translated) == 'Union[Required[Any], Alias[Any]]'


def test_type_translator_rewrites_callable_and_typed_dict() -> None:
    callable_type = types.CallableType(
        [types.NoneType()],
        [symbols.ArgKind.POS],
        [None],
        types.NoneType(),
        make_instance('function'),
    )
    typed_dict = types.TypedDictType(
        {'cb': callable_type, 'value': types.NoneType()},
        {'cb'},
        set(),
        make_instance('dict'),
    )

    translated = typed_dict.accept(NoneToAnyTranslator())

    assert str(translated) == "TypedDict({'cb': def (Any) -> Any, 'value'?: Any})"
