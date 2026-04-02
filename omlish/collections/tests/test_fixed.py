import pytest

from ..fixed import FixedMapping


def test_basic_mapping_behavior() -> None:
    fm = FixedMapping({'a': 0, 'b': 1, 'c': 2}, [10, 20, 30])

    assert len(fm) == 3
    assert list(fm) == ['a', 'b', 'c']

    assert fm['a'] == 10
    assert fm['b'] == 20
    assert fm['c'] == 30

    assert 'a' in fm
    assert 'z' not in fm


def test_getitem_missing_key_raises_key_error() -> None:
    fm = FixedMapping({'a': 0}, [10])

    with pytest.raises(KeyError):
        _ = fm['missing']


def test_debug_property_returns_materialized_dict() -> None:
    fm = FixedMapping({'a': 0, 'b': 1}, [10, 20])

    assert fm.debug == {'a': 10, 'b': 20}
    assert isinstance(fm.debug, dict)


def test_itervalues() -> None:
    fm = FixedMapping({'a': 0, 'b': 1, 'c': 2}, [10, 20, 30])

    assert list(fm.itervalues()) == [10, 20, 30]


def test_iteritems() -> None:
    fm = FixedMapping({'a': 0, 'b': 1, 'c': 2}, [10, 20, 30])

    assert list(fm.iteritems()) == [('a', 10), ('b', 20), ('c', 30)]


def test_keys_values_items_views() -> None:
    fm = FixedMapping({'a': 0, 'b': 1}, [10, 20])

    assert list(fm.keys()) == ['a', 'b']
    assert list(fm.values()) == [10, 20]
    assert list(fm.items()) == [('a', 10), ('b', 20)]

    assert 'a' in fm.keys()  # noqa
    assert 10 in fm.values()
    assert ('a', 10) in fm.items()

    assert ('a', 11) not in fm.items()
    assert ('z', 10) not in fm.items()


def test_dict_constructor_round_trip() -> None:
    fm = FixedMapping({'a': 0, 'b': 1, 'c': 2}, [10, 20, 30])

    assert dict(fm) == {'a': 10, 'b': 20, 'c': 30}


def test_equality_with_dict() -> None:
    fm = FixedMapping({'a': 0, 'b': 1}, [10, 20])

    assert fm == {'a': 10, 'b': 20}
    assert {'a': 10, 'b': 20} == fm  # type: ignore[unreachable]
    assert fm != {'a': 10, 'b': 21}
    assert fm != {'a': 10}
    assert fm != {'a': 10, 'b': 20, 'c': 30}


def test_hash_matches_tuple_zip_definition() -> None:
    keys = {'a': 0, 'b': 1, 'c': 2}
    values = [10, 20, 30]
    fm = FixedMapping(keys, values)

    expected = hash(tuple(zip(keys, values, strict=True)))
    assert hash(fm) == expected


def test_hash_is_cached() -> None:
    fm = FixedMapping({'a': 0, 'b': 1}, [10, 20])

    assert not hasattr(fm, '_hash')

    h1 = hash(fm)
    assert hasattr(fm, '_hash')

    h2 = hash(fm)
    assert h1 == h2
    assert fm._hash == h1  # noqa


def test_empty_mapping() -> None:
    fm: FixedMapping = FixedMapping({}, [])

    assert len(fm) == 0
    assert list(fm) == []
    assert list(fm.itervalues()) == []
    assert list(fm.iteritems()) == []
    assert fm.debug == {}
    assert dict(fm) == {}


def test_mismatched_keys_and_values_length_raises_in_iteritems() -> None:
    fm = FixedMapping({'a': 0, 'b': 1}, [10])

    with pytest.raises(ValueError):  # noqa
        list(fm.iteritems())


def test_mismatched_keys_and_values_length_raises_in_hash() -> None:
    fm = FixedMapping({'a': 0, 'b': 1}, [10])

    with pytest.raises(ValueError):  # noqa
        hash(fm)


def test_len_comes_from_values() -> None:
    fm = FixedMapping({'a': 0}, [10, 20])

    assert len(fm) == 2
    assert list(fm) == ['a']

    # This is intentionally unchecked
    assert fm['a'] == 10


def test_key_indexing_controls_lookup_not_iteration_position() -> None:
    fm = FixedMapping({'a': 2, 'b': 0, 'c': 1}, [10, 20, 30])

    assert list(fm) == ['a', 'b', 'c']
    assert list(fm.itervalues()) == [10, 20, 30]
    assert list(fm.iteritems()) == [('a', 10), ('b', 20), ('c', 30)]

    # But direct lookup uses the integer index mapping.
    assert fm['a'] == 30
    assert fm['b'] == 10
    assert fm['c'] == 20


def test_debug_uses_key_indices_not_zip_pairing() -> None:
    fm = FixedMapping({'a': 2, 'b': 0, 'c': 1}, [10, 20, 30])

    assert fm.debug == {'a': 30, 'b': 10, 'c': 20}


def test_out_of_range_index_raises_index_error() -> None:
    fm = FixedMapping({'a': 5}, [10, 20])

    with pytest.raises(IndexError):
        _ = fm['a']

    with pytest.raises(IndexError):
        _ = fm.debug


def test_values_view_reflects_iteration_order_of_values_sequence() -> None:
    fm = FixedMapping({'x': 1, 'y': 0}, ['v0', 'v1'])

    assert list(fm.values()) == ['v0', 'v1']


def test_items_view_reflects_zip_of_key_iteration_and_values_sequence() -> None:
    fm = FixedMapping({'x': 1, 'y': 0}, ['v0', 'v1'])

    assert list(fm.items()) == [('x', 'v0'), ('y', 'v1')]
