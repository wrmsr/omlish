# ruff: noqa: F821 PLC0132 SLF001
import collections.abc as cabc
import threading
import typing as ta

from ..core import symbols
from ..core import types
from ..universe import TypeUniverse


class LocalThing:
    pass


def test_runtime_universe_returns_stable_type_info_for_runtime_class() -> None:
    universe = TypeUniverse(
        lock=threading.RLock(),
    )

    assert universe.get_type_info(list) is universe.get_type_info(list)
    assert universe.get_type_info('builtins.list') is universe.get_type_info(list)


def test_runtime_universe_uses_known_builtin_and_collections_fullnames() -> None:
    universe = TypeUniverse(
        lock=threading.RLock(),
    )

    assert universe.get_type_info(list).fullname == 'builtins.list'
    assert universe.get_type_info(dict).fullname == 'builtins.dict'
    assert universe.get_type_info(cabc.Sequence).fullname == 'collections.abc.Sequence'
    assert universe.get_type_info(cabc.Mapping).fullname == 'collections.abc.Mapping'
    assert universe.get_type_info(ta.Generic).fullname == 'typing.Generic'


def test_runtime_universe_adds_generic_type_vars() -> None:
    universe = TypeUniverse(
        lock=threading.RLock(),
    )

    list_info = universe.get_type_info(list)
    dict_info = universe.get_type_info(dict)
    sequence_info = universe.get_type_info(cabc.Sequence)

    assert [tv.name for tv in list_info.type_vars] == ['T0']
    assert [tv.name for tv in dict_info.type_vars] == ['T0', 'T1']
    assert dict_info.variances == (symbols.VarianceKind.IN, symbols.VarianceKind.IN)
    assert sequence_info.variances == (symbols.VarianceKind.CO,)
    assert sequence_info.type_vars[0].upper_bound.type is universe.get_type_info(object)  # type: ignore


def test_runtime_universe_adds_known_collection_abc_bases() -> None:
    universe = TypeUniverse(
        lock=threading.RLock(),
    )

    str_info = universe.get_type_info(str)
    bytes_info = universe.get_type_info(bytes)
    int_info = universe.get_type_info(int)
    list_info = universe.get_type_info(list)
    tuple_info = universe.get_type_info(tuple)
    dict_info = universe.get_type_info(dict)
    set_info = universe.get_type_info(set)
    frozenset_info = universe.get_type_info(frozenset)
    mutable_sequence_info = universe.get_type_info(cabc.MutableSequence)
    sequence_info = universe.get_type_info(cabc.Sequence)
    iterable_info = universe.get_type_info(cabc.Iterable)
    mutable_mapping_info = universe.get_type_info(cabc.MutableMapping)
    mapping_info = universe.get_type_info(cabc.Mapping)
    mutable_set_info = universe.get_type_info(cabc.MutableSet)
    set_abc_info = universe.get_type_info(cabc.Set)

    assert [info.fullname for info in list_info.mro] == [
        'builtins.list',
        'collections.abc.MutableSequence',
        'collections.abc.Sequence',
        'collections.abc.Iterable',
        'builtins.object',
    ]
    assert len(list_info.bases) == 1
    str_base = str_info.bases[0]
    assert isinstance(str_base, types.Instance)
    assert str_base.type is sequence_info
    assert len(str_base.args) == 1
    assert isinstance(str_base.args[0], types.Instance)
    assert str_base.args[0].type is str_info

    bytes_base = bytes_info.bases[0]
    assert isinstance(bytes_base, types.Instance)
    assert bytes_base.type is sequence_info
    assert len(bytes_base.args) == 1
    assert isinstance(bytes_base.args[0], types.Instance)
    assert bytes_base.args[0].type is int_info

    list_base = list_info.bases[0]
    assert isinstance(list_base, types.Instance)
    assert list_base.type is mutable_sequence_info
    assert list_base.args == (list_info.type_vars[0],)

    sequence_base = sequence_info.bases[0]
    assert isinstance(sequence_base, types.Instance)
    assert sequence_base.type is iterable_info

    tuple_base = tuple_info.bases[0]
    assert isinstance(tuple_base, types.Instance)
    assert tuple_base.type is sequence_info
    assert tuple_base.args == (tuple_info.type_vars[0],)

    dict_base = dict_info.bases[0]
    assert isinstance(dict_base, types.Instance)
    assert dict_base.type is mutable_mapping_info
    assert dict_base.args == dict_info.type_vars

    mapping_base = mapping_info.bases[0]
    assert isinstance(mapping_base, types.Instance)
    assert mapping_base.type is iterable_info
    assert mapping_base.args == (mapping_info.type_vars[0],)

    set_base = set_info.bases[0]
    assert isinstance(set_base, types.Instance)
    assert set_base.type is mutable_set_info
    assert set_base.args == (set_info.type_vars[0],)

    frozenset_base = frozenset_info.bases[0]
    assert isinstance(frozenset_base, types.Instance)
    assert frozenset_base.type is set_abc_info
    assert frozenset_base.args == (frozenset_info.type_vars[0],)


def test_runtime_universe_assigns_id_qualified_fullname_for_dynamic_classes() -> None:
    universe = TypeUniverse(
        lock=threading.RLock(),
    )

    info = universe.get_type_info(LocalThing)

    assert info.fullname.startswith(f'{__name__}.LocalThing@')
    assert universe.get_type_info(LocalThing) is info


def test_runtime_universe_can_assign_deterministic_counter_dynamic_names() -> None:
    universe = TypeUniverse(
        dynamic_type_name_suffix='counter',
        lock=threading.RLock(),
    )

    class LocalOne:
        pass

    class LocalTwo:
        pass

    one_info = universe.get_type_info(LocalOne)
    two_info = universe.get_type_info(LocalTwo)

    assert one_info.fullname.endswith('.LocalOne@1')
    assert two_info.fullname.endswith('.LocalTwo@2')
    assert universe.get_type_info(LocalOne) is one_info


def test_runtime_universe_keeps_same_name_dynamic_classes_distinct() -> None:
    universe = TypeUniverse(
        dynamic_type_name_suffix='counter',
        lock=threading.RLock(),
    )

    left = type('Repeated', (), {'__module__': __name__})
    right = type('Repeated', (), {'__module__': __name__})

    left_info = universe.get_type_info(left)
    right_info = universe.get_type_info(right)

    assert left_info is not right_info
    assert left_info.fullname == f'{__name__}.Repeated@1'
    assert right_info.fullname == f'{__name__}.Repeated@2'


def test_runtime_universe_keeps_newtype_runtime_object() -> None:
    universe = TypeUniverse(
        lock=threading.RLock(),
    )
    user_id = ta.NewType('UserId', int)  # type: ignore

    info = universe.get_newtype_info(user_id)

    assert info.fullname == f'{__name__}.UserId'
    assert universe.get_runtime_type(info) is user_id
    assert [base.type.fullname for base in info.bases if isinstance(base, types.Instance)] == ['builtins.int']


def test_default_runtime_universe_helper_is_stable() -> None:
    universe = TypeUniverse(
        lock=threading.RLock(),
    )
    assert universe.get_type_info(tuple) is universe.get_type_info(tuple)
    assert universe.get_type_info(tuple).fullname == 'builtins.tuple'
