import pytest

from ..fixedmap import FixedMap
from ..fixedmap import new_fixed_map


def test_basic_mapping_behavior() -> None:
    fm = new_fixed_map({'a': 10, 'b': 20, 'c': 30})

    assert len(fm) == 3
    assert list(fm) == ['a', 'b', 'c']

    assert fm['a'] == 10
    assert fm['b'] == 20
    assert fm['c'] == 30

    assert 'a' in fm
    assert 'z' not in fm


def test_getitem_missing_key_raises_key_error() -> None:
    fm = new_fixed_map({'a': 10})

    with pytest.raises(KeyError):
        _ = fm['missing']


def test_debug_property_returns_materialized_dict() -> None:
    fm = new_fixed_map({'a': 10, 'b': 20})

    assert fm.debug == {'a': 10, 'b': 20}
    assert isinstance(fm.debug, dict)


def test_itervalues() -> None:
    fm = new_fixed_map({'a': 10, 'b': 20, 'c': 30})

    assert list(fm.itervalues()) == [10, 20, 30]


def test_iteritems() -> None:
    fm = new_fixed_map({'a': 10, 'b': 20, 'c': 30})

    assert list(fm.iteritems()) == [('a', 10), ('b', 20), ('c', 30)]


def test_keys_values_items_views() -> None:
    fm = new_fixed_map({'a': 10, 'b': 20})

    assert list(fm.keys()) == ['a', 'b']
    assert list(fm.values()) == [10, 20]
    assert list(fm.items()) == [('a', 10), ('b', 20)]

    assert 'a' in fm.keys()  # noqa
    assert 10 in fm.values()
    assert ('a', 10) in fm.items()

    assert ('a', 11) not in fm.items()
    assert ('z', 10) not in fm.items()


def test_dict_constructor_round_trip() -> None:
    fm = new_fixed_map({'a': 10, 'b': 20, 'c': 30})

    assert dict(fm) == {'a': 10, 'b': 20, 'c': 30}


def test_equality_with_dict() -> None:
    fm = new_fixed_map({'a': 10, 'b': 20})

    assert fm == {'a': 10, 'b': 20}
    assert {'a': 10, 'b': 20} == fm  # type: ignore[unreachable]
    assert fm != {'a': 10, 'b': 21}
    assert fm != {'a': 10}
    assert fm != {'a': 10, 'b': 20, 'c': 30}


def test_hash_matches_tuple_zip_definition() -> None:
    keys = {'a': 0, 'b': 1, 'c': 2}
    values = [10, 20, 30]
    fm = new_fixed_map(zip(keys, values))

    expected = hash(tuple(zip(keys, values, strict=True)))
    assert hash(fm) == expected


def test_hash_is_cached() -> None:
    fm = new_fixed_map({'a': 10, 'b': 20})

    assert not hasattr(fm, '_hash')

    h1 = hash(fm)
    assert hasattr(fm, '_hash')

    h2 = hash(fm)
    assert h1 == h2
    assert fm._hash == h1  # noqa


def test_empty_mapping() -> None:
    fm: FixedMap = new_fixed_map({})

    assert len(fm) == 0
    assert list(fm) == []
    assert list(fm.itervalues()) == []
    assert list(fm.iteritems()) == []
    assert fm.debug == {}
    assert dict(fm) == {}


def test_debug() -> None:
    fm = new_fixed_map({'a': 30, 'b': 10, 'c': 20})

    assert fm.debug == {'a': 30, 'b': 10, 'c': 20}
