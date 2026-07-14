# ruff: noqa: SLF001
from ..subtypes import is_same_type
from ..subtypes import is_subtype
from ..types import Instance
from ..types import LiteralType
from .helpers import make_info
from .helpers import make_instance


def test_literal_type_is_subtype_of_fallback_and_object() -> None:
    object_info = make_info('builtins.object')
    str_info = make_info('builtins.str')
    str_info._mro = (str_info, object_info)
    literal = LiteralType('x', Instance(str_info, []))

    assert is_subtype(literal, Instance(str_info, []))
    assert is_subtype(literal, Instance(object_info, []))


def test_literal_type_subtype_preserves_literal_value_identity() -> None:
    str_info = make_info('builtins.str')
    left = LiteralType('x', Instance(str_info, []))
    same = LiteralType('x', Instance(str_info, []))
    different = LiteralType('y', Instance(str_info, []))

    assert is_subtype(left, same)
    assert is_same_type(left, same)
    assert not is_subtype(left, different)
    assert not is_same_type(left, different)


def test_literal_type_is_not_supertype_of_fallback() -> None:
    str_info = make_info('builtins.str')
    literal = LiteralType('x', Instance(str_info, []))

    assert not is_subtype(make_instance(str_info), literal)
