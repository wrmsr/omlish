import typing as ta

import pytest

from .... import lang
from .. import _fixedmap_py
from .. import fixedmap
from ..fixedmap import FixedMap
from ..fixedmap import new_fixed_map


class _BaseFixedMapTests:
    _impl = None

    @pytest.fixture(scope='class', autouse=True)
    @classmethod
    def class_setup_teardown(cls):
        old_impl = fixedmap._impl  # noqa
        fixedmap._impl = cls._impl  # noqa
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
        assert {'a': 10, 'b': 20} == fm
        assert fm != {'a': 10, 'b': 21}
        assert fm != {'a': 10}
        assert fm != {'a': 10, 'b': 20, 'c': 30}

    def test_equality_with_non_mappings(self) -> None:
        fm = new_fixed_map({'a': 10, 'b': 20})

        for other in (42, 'ab', [10, 20], None, {'a', 'b'}):
            assert fm != other
            assert other != fm
            assert not (fm == other)  # noqa

    def test_isinstance_mapping(self) -> None:
        fm = new_fixed_map({'a': 10})

        assert isinstance(fm, ta.Mapping)
        assert isinstance(fm.fixed_keys, ta.Mapping)

    def test_hash_is_key_order_insensitive(self) -> None:
        fm1 = new_fixed_map({'a': 10, 'b': 20})
        fm2 = new_fixed_map({'b': 20, 'a': 10})

        assert fm1 == fm2
        assert hash(fm1) == hash(fm2)

    def test_ctor_rejects_kwargs(self) -> None:
        with pytest.raises(TypeError):
            self._impl.FixedMapKeys(['a'], bogus=1)  # type: ignore  # noqa

    def test_keys_debug_is_immutable(self) -> None:
        fm = new_fixed_map({'a': 10})

        with pytest.raises(TypeError):
            fm.fixed_keys.debug['b'] = 1  # type: ignore  # noqa

    def test_duplicate_key(self) -> None:
        with pytest.raises(lang.DuplicateKeyError):
            new_fixed_map([('a', 1), ('b', 2), ('a', 3)])

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

    def test_cross_impl_equality_and_hash():
        items = [('a', 10), ('b', (1, 'two')), (3, 'c')]

        cfm = _fixedmap.FixedMap(_fixedmap.FixedMapKeys([k for k, _ in items]), [v for _, v in items])
        pfm = _fixedmap_py.FixedMap(_fixedmap_py.FixedMapKeys([k for k, _ in items]), [v for _, v in items])

        assert cfm == pfm
        assert pfm == cfm
        assert hash(cfm) == hash(pfm)

        # And with differing key order on top.
        cfm2 = _fixedmap.FixedMap(_fixedmap.FixedMapKeys([k for k, _ in reversed(items)]), [v for _, v in reversed(items)])  # noqa

        assert cfm2 == pfm
        assert hash(cfm2) == hash(pfm)
