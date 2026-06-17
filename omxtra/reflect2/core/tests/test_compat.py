# ruff: noqa: SLF001
import pytest

from ...errors import UnsupportedTypeOperationError
from .. import symbols
from .. import types
from ..compat import is_assignable
from ..compat import is_assignable_or_false


def make_any() -> types.AnyType:
    return types.AnyType(types.TypeOfAny.EXPLICIT)


def make_info(name: str) -> symbols.TypeInfo:
    return symbols.TypeInfo(name, name)


def make_instance(info: symbols.TypeInfo, args: list[types.Type] | None = None) -> types.Instance:
    return types.Instance(info, [] if args is None else args)


def test_is_assignable_uses_subtype_direction() -> None:
    base_info = make_info('Base')
    child_info = make_info('Child')
    child_info._mro = (child_info, base_info)

    assert is_assignable(make_instance(child_info), make_instance(base_info))
    assert not is_assignable(make_instance(base_info), make_instance(child_info))


def test_is_assignable_keeps_any_compatibility() -> None:
    any_type = make_any()
    int_type = make_instance(make_info('int'))

    assert is_assignable(any_type, int_type)
    assert is_assignable(int_type, any_type)


def test_is_assignable_raises_for_unsupported_relation() -> None:
    fallback = make_instance(make_info('function'))
    callable_type = types.CallableType([], [], [], make_any(), fallback)

    with pytest.raises(UnsupportedTypeOperationError):
        is_assignable(callable_type, make_instance(make_info('object')))


def test_is_assignable_or_false_is_conservative_for_unsupported_relation() -> None:
    fallback = make_instance(make_info('function'))
    callable_type = types.CallableType([], [], [], make_any(), fallback)

    assert not is_assignable_or_false(callable_type, make_instance(make_info('object')))
