import typing as ta

from ...core.typekeys import type_key
from ...reflect import RuntimeTypeReflector
from ...universe import RuntimeTypeUniverse
from ..ops import reflect_is_assignable
from ..ops import reflect_is_same_type


def _make_reflector() -> RuntimeTypeReflector:
    return RuntimeTypeReflector(RuntimeTypeUniverse())


def test_runtime_new_type_is_assignable_to_supertype_and_object() -> None:
    user_id = ta.NewType('UserId', int)  # type: ignore  # noqa
    reflector = _make_reflector()

    assert reflect_is_assignable(user_id, int, reflector)
    assert reflect_is_assignable(user_id, object, reflector)


def test_runtime_literal_new_type_is_assignable_to_object() -> None:
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore  # noqa
    reflector = _make_reflector()

    assert reflect_is_assignable(mode, object, reflector)


def test_runtime_distinct_new_types_remain_nominally_distinct() -> None:
    user_id = ta.NewType('UserId', int)  # type: ignore  # noqa
    account_id = ta.NewType('AccountId', int)  # type: ignore  # noqa
    reflector = _make_reflector()

    assert not reflect_is_same_type(user_id, account_id, reflector)
    assert not reflect_is_assignable(user_id, account_id, reflector)
    assert not reflect_is_assignable(account_id, user_id, reflector)


def test_runtime_new_type_keys_still_preserve_identity() -> None:
    user_id = ta.NewType('UserId', int)  # type: ignore  # noqa
    account_id = ta.NewType('AccountId', int)  # type: ignore  # noqa
    reflector = _make_reflector()

    user_type = reflector.reflect_type(user_id)
    account_type = reflector.reflect_type(account_id)
    int_type = reflector.reflect_type(int)

    assert type_key(user_type) != type_key(account_type)
    assert type_key(user_type) != type_key(int_type)
