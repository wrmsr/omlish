import pytest

from .. import _fixedmap_py
from .. import fixedmap
from ..fixedmap import FixedMap
from ..fixedmap import new_fixed_map


class _BaseFixedMapTests:
    _impl = None

    @pytest.fixture(scope='class', autouse=True)
    def class_setup_teardown(self):
        old_impl = fixedmap._impl  # noqa
        fixedmap._impl = self._impl  # noqa
        yield
        fixedmap._impl = old_impl  # noqa

    def test_basic_mapping_behavior(self) -> None:
        fm = new_fixed_map({'a': 10, 'b': 20, 'c': 30})

        assert len(fm) == 3
        assert list(fm) == ['a', 'b', 'c']

        assert fm['a'] == 10
        assert fm['b'] == 20
        assert fm['c'] == 30

        assert 'a' in fm
        assert 'z' not in fm

    def test_getitem_missing_key_raises_key_error(self) -> None:
        fm = new_fixed_map({'a': 10})

        with pytest.raises(KeyError):
            _ = fm['missing']

    def test_debug_property_returns_materialized_dict(self) -> None:
        fm = new_fixed_map({'a': 10, 'b': 20})

        assert fm.debug == {'a': 10, 'b': 20}
        assert isinstance(fm.debug, dict)

    def test_itervalues(self) -> None:
        fm = new_fixed_map({'a': 10, 'b': 20, 'c': 30})

        assert list(fm.itervalues()) == [10, 20, 30]

    def test_iteritems(self) -> None:
        fm = new_fixed_map({'a': 10, 'b': 20, 'c': 30})

        assert list(fm.iteritems()) == [('a', 10), ('b', 20), ('c', 30)]

    def test_keys_values_items_views(self) -> None:
        fm = new_fixed_map({'a': 10, 'b': 20})

        assert list(fm.keys()) == ['a', 'b']
        assert list(fm.values()) == [10, 20]
        assert list(fm.items()) == [('a', 10), ('b', 20)]

        assert 'a' in fm.keys()  # noqa
        assert 10 in fm.values()
        assert ('a', 10) in fm.items()

        assert ('a', 11) not in fm.items()
        assert ('z', 10) not in fm.items()

    def test_dict_constructor_round_trip(self) -> None:
        fm = new_fixed_map({'a': 10, 'b': 20, 'c': 30})

        assert dict(fm) == {'a': 10, 'b': 20, 'c': 30}

    def test_equality_with_dict(self) -> None:
        fm = new_fixed_map({'a': 10, 'b': 20})

        assert fm == {'a': 10, 'b': 20}
        assert {'a': 10, 'b': 20} == fm  # type: ignore[unreachable]
        assert fm != {'a': 10, 'b': 21}
        assert fm != {'a': 10}
        assert fm != {'a': 10, 'b': 20, 'c': 30}

    # def test_hash_matches_tuple_zip_definition(self) -> None:
    #     keys = {'a': 0, 'b': 1, 'c': 2}
    #     values = [10, 20, 30]
    #     fm = new_fixed_map(zip(keys, values))
    #
    #     expected = hash(tuple(zip(keys, values, strict=True)))
    #     assert hash(fm) == expected

    def test_hash_is_cached(self) -> None:
        class MyHashable:
            c = 0

            def __hash__(self):
                self.c += 1
                return 420

        fm = new_fixed_map({'a': 10, 'b': 20, 'h': (mh := MyHashable())})
        assert mh.c == 0

        h1 = hash(fm)
        assert mh.c == 1

        h2 = hash(fm)
        assert h1 == h2
        assert mh.c == 1

    def test_empty_mapping(self) -> None:
        fm: FixedMap = new_fixed_map({})

        assert len(fm) == 0
        assert list(fm) == []
        assert list(fm.itervalues()) == []
        assert list(fm.iteritems()) == []
        assert fm.debug == {}
        assert dict(fm) == {}

    def test_debug(self) -> None:
        fm = new_fixed_map({'a': 30, 'b': 10, 'c': 20})

        assert fm.debug == {'a': 30, 'b': 10, 'c': 20}


class TestPyFixedMap(_BaseFixedMapTests):
    _impl = _fixedmap_py  # type: ignore


try:
    from .. import _fixedmap  # type: ignore
except ImportError:
    pass
else:
    class TestCFixedMap(_BaseFixedMapTests):
        _impl = _fixedmap
