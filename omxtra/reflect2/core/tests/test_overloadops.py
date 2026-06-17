# ruff: noqa: PLC0132 SLF001
import pytest

from ...errors import UnsupportedTypeOperationError
from ..join import join_types
from ..meet import meet_types
from ..strconv import type_str
from ..subtypes import is_subtype
from ..symbols import ArgKind
from ..types import CallableType
from ..types import Instance
from ..types import Overloaded
from .helpers import make_info
from .helpers import make_instance
from .helpers import make_type_var


def _callable(arg: Instance, ret: Instance, fallback: Instance) -> CallableType:
    return CallableType([arg], [ArgKind.POS], [None], ret, fallback)


def _named_callable(arg: Instance, ret: Instance, fallback: Instance) -> CallableType:
    return CallableType([arg], [ArgKind.NAMED], ['value'], ret, fallback)


def _overloaded(*items: CallableType) -> Overloaded:
    return Overloaded(list(items))


def test_same_overload_is_subtype_via_exact_type_match() -> None:
    fallback = make_instance(make_info('function'))
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))
    left = _overloaded(
        _callable(int_type, int_type, fallback),
        _callable(str_type, str_type, fallback),
    )
    right = _overloaded(*left.items)

    assert is_subtype(left, right)


def test_pairwise_overload_subtyping_uses_callable_subtyping_in_order() -> None:
    object_info = make_info('builtins.object')
    int_info = make_info('builtins.int')
    int_info._mro = (int_info, object_info)
    str_info = make_info('builtins.str')
    str_info._mro = (str_info, object_info)
    fallback = make_instance(make_info('function'))
    object_type = make_instance(object_info)
    int_type = make_instance(int_info)
    str_type = make_instance(str_info)
    left = _overloaded(
        _callable(object_type, int_type, fallback),
        _callable(object_type, str_type, fallback),
    )
    right = _overloaded(
        _callable(int_type, object_type, fallback),
        _callable(str_type, object_type, fallback),
    )

    assert is_subtype(left, right)
    assert not is_subtype(right, left)


def test_pairwise_overload_subtyping_preserves_item_order() -> None:
    fallback = make_instance(make_info('function'))
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))
    left = _overloaded(
        _callable(int_type, int_type, fallback),
        _callable(str_type, str_type, fallback),
    )
    right = _overloaded(
        _callable(str_type, str_type, fallback),
        _callable(int_type, int_type, fallback),
    )

    assert not is_subtype(left, right)


def test_overload_subtyping_fails_closed_for_mismatched_item_counts() -> None:
    fallback = make_instance(make_info('function'))
    int_type = make_instance(make_info('builtins.int'))
    left = _overloaded(
        _callable(int_type, int_type, fallback),
        _callable(int_type, int_type, fallback),
    )
    right = _overloaded(_callable(int_type, int_type, fallback))

    with pytest.raises(UnsupportedTypeOperationError, match='mismatched item counts'):
        is_subtype(left, right)


def test_overload_subtype_of_callable_uses_any_matching_item() -> None:
    fallback = make_instance(make_info('function'))
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))
    overloaded = _overloaded(
        _callable(str_type, str_type, fallback),
        _callable(int_type, int_type, fallback),
    )

    assert is_subtype(overloaded, _callable(int_type, int_type, fallback))
    assert not is_subtype(overloaded, _callable(make_instance(make_info('builtins.bytes')), int_type, fallback))


def test_callable_subtype_of_overload_must_satisfy_all_items() -> None:
    object_info = make_info('builtins.object')
    int_info = make_info('builtins.int')
    str_info = make_info('builtins.str')
    int_info._mro = (int_info, object_info)
    str_info._mro = (str_info, object_info)
    fallback = make_instance(make_info('function'))
    object_type = make_instance(object_info)
    int_type = make_instance(int_info)
    str_type = make_instance(str_info)
    overloaded = _overloaded(
        _callable(int_type, object_type, fallback),
        _callable(str_type, object_type, fallback),
    )

    assert is_subtype(_callable(object_type, int_type, fallback), overloaded)
    assert not is_subtype(_callable(int_type, int_type, fallback), overloaded)


def test_overload_and_callable_subtyping_fail_closed_for_generic_callable_items() -> None:
    fallback = make_instance(make_info('function'))
    int_type = make_instance(make_info('builtins.int'))
    t_var = make_type_var('T', 1)
    generic_callable = CallableType([t_var], [ArgKind.POS], [None], t_var, fallback, variables=[t_var])
    overloaded = _overloaded(generic_callable)

    with pytest.raises(UnsupportedTypeOperationError, match='Unsupported Overloaded subtype relation'):
        is_subtype(overloaded, _callable(int_type, int_type, fallback))

    with pytest.raises(UnsupportedTypeOperationError, match='generic Callable'):
        is_subtype(_callable(int_type, int_type, fallback), overloaded)


def test_same_overload_meet_and_join_return_left() -> None:
    fallback = make_instance(make_info('function'))
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))
    left = _overloaded(
        _callable(int_type, int_type, fallback),
        _callable(str_type, str_type, fallback),
    )
    right = _overloaded(*left.items)

    assert meet_types(left, right) is left
    assert join_types(left, right) is left


def test_pairwise_overload_meet_and_join_synthesize_items_in_order() -> None:
    object_info = make_info('builtins.object')
    base_info = make_info('Base')
    base_info._mro = (base_info, object_info)
    child_info = make_info('Child')
    child_info._mro = (child_info, base_info, object_info)
    fallback = make_instance(make_info('function'))
    base = make_instance(base_info)
    child = make_instance(child_info)
    left = _overloaded(
        _callable(base, base, fallback),
        _callable(child, child, fallback),
    )
    right = _overloaded(
        _callable(child, child, fallback),
        _callable(base, base, fallback),
    )

    met = meet_types(left, right)
    joined = join_types(left, right)

    assert isinstance(met, Overloaded)
    assert isinstance(joined, Overloaded)
    assert [type_str(item) for item in met.items] == [
        'def (Base) -> Child',
        'def (Base) -> Child',
    ]
    assert [type_str(item) for item in joined.items] == [
        'def (Child) -> Base',
        'def (Child) -> Base',
    ]


def test_overload_meet_and_join_fail_closed_for_mismatched_item_counts() -> None:
    fallback = make_instance(make_info('function'))
    int_type = make_instance(make_info('builtins.int'))
    left = _overloaded(
        _callable(int_type, int_type, fallback),
        _callable(int_type, int_type, fallback),
    )
    right = _overloaded(_callable(int_type, int_type, fallback))

    with pytest.raises(UnsupportedTypeOperationError, match='mismatched item counts'):
        meet_types(left, right)

    with pytest.raises(UnsupportedTypeOperationError, match='mismatched item counts'):
        join_types(left, right)


def test_overload_meet_and_join_fail_closed_for_mismatched_callable_shapes() -> None:
    fallback = make_instance(make_info('function'))
    int_type = make_instance(make_info('builtins.int'))
    left = _overloaded(_callable(int_type, int_type, fallback))
    right = _overloaded(_named_callable(int_type, int_type, fallback))

    with pytest.raises(UnsupportedTypeOperationError, match='Unsupported Overloaded meet'):
        meet_types(left, right)

    with pytest.raises(UnsupportedTypeOperationError, match='Unsupported Overloaded join'):
        join_types(left, right)


def test_overload_and_callable_meet_and_join_use_subtype_bounds_when_supported() -> None:
    fallback = make_instance(make_info('function'))
    int_type = make_instance(make_info('builtins.int'))
    callable_type = _callable(int_type, int_type, fallback)
    overloaded = _overloaded(callable_type)

    assert meet_types(overloaded, callable_type) is overloaded
    assert meet_types(callable_type, overloaded) is callable_type
    assert join_types(overloaded, callable_type) is callable_type
    assert join_types(callable_type, overloaded) is overloaded


def test_overload_and_callable_meet_and_join_fail_closed_for_generic_callable_items() -> None:
    fallback = make_instance(make_info('function'))
    int_type = make_instance(make_info('builtins.int'))
    t_var = make_type_var('T', 1)
    callable_type = _callable(int_type, int_type, fallback)
    generic_callable = CallableType([t_var], [ArgKind.POS], [None], t_var, fallback, variables=[t_var])
    overloaded = _overloaded(generic_callable)

    with pytest.raises(UnsupportedTypeOperationError, match='Unsupported meet'):
        meet_types(overloaded, callable_type)

    with pytest.raises(UnsupportedTypeOperationError, match='Unsupported join'):
        join_types(overloaded, callable_type)
