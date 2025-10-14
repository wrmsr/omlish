import pytest


try:
    from .. import _hamt  # type: ignore
except ImportError:
    pytest.skip('_hamt module not built', allow_module_level=True)


class TestHamtBasics:
    def test_new(self):
        h = _hamt.new()
        assert h is not None
        assert _hamt.len(h) == 0

    def test_assoc_single(self):
        h1 = _hamt.new()
        h2 = _hamt.assoc(h1, 'key', 'value')

        assert _hamt.len(h1) == 0  # original unchanged
        assert _hamt.len(h2) == 1
        assert _hamt.find(h2, 'key') == 'value'

    def test_assoc_multiple(self):
        h = _hamt.new()
        h = _hamt.assoc(h, 'a', 1)
        h = _hamt.assoc(h, 'b', 2)
        h = _hamt.assoc(h, 'c', 3)

        assert _hamt.len(h) == 3
        assert _hamt.find(h, 'a') == 1
        assert _hamt.find(h, 'b') == 2
        assert _hamt.find(h, 'c') == 3

    def test_assoc_overwrite(self):
        h1 = _hamt.new()
        h2 = _hamt.assoc(h1, 'key', 'old')
        h3 = _hamt.assoc(h2, 'key', 'new')

        assert _hamt.len(h2) == 1
        assert _hamt.len(h3) == 1
        assert _hamt.find(h2, 'key') == 'old'
        assert _hamt.find(h3, 'key') == 'new'

    def test_without(self):
        h1 = _hamt.new()
        h2 = _hamt.assoc(h1, 'key', 'value')
        h3 = _hamt.without(h2, 'key')

        assert _hamt.len(h2) == 1  # original unchanged
        assert _hamt.len(h3) == 0
        assert _hamt.find(h2, 'key') == 'value'
        assert _hamt.find(h3, 'key') is None

    def test_without_multiple(self):
        h = _hamt.new()
        h = _hamt.assoc(h, 'a', 1)
        h = _hamt.assoc(h, 'b', 2)
        h = _hamt.assoc(h, 'c', 3)

        h = _hamt.without(h, 'b')
        assert _hamt.len(h) == 2
        assert _hamt.find(h, 'a') == 1
        assert _hamt.find(h, 'b') is None
        assert _hamt.find(h, 'c') == 3

    def test_without_nonexistent(self):
        h1 = _hamt.new()
        h2 = _hamt.without(h1, 'nonexistent')
        # Should not raise, just return equivalent hamt
        assert _hamt.len(h2) == 0


class TestHamtFind:
    def test_find_existing(self):
        h = _hamt.new()
        h = _hamt.assoc(h, 'key', 'value')
        assert _hamt.find(h, 'key') == 'value'

    def test_find_nonexistent(self):
        h = _hamt.new()
        assert _hamt.find(h, 'key') is None

    def test_find_various_types(self):
        h = _hamt.new()
        h = _hamt.assoc(h, 'str', 'string')
        h = _hamt.assoc(h, 42, 'int')
        h = _hamt.assoc(h, (1, 2), 'tuple')

        assert _hamt.find(h, 'str') == 'string'
        assert _hamt.find(h, 42) == 'int'
        assert _hamt.find(h, (1, 2)) == 'tuple'


class TestHamtEquality:
    def test_eq_empty(self):
        h1 = _hamt.new()
        h2 = _hamt.new()
        assert _hamt.eq(h1, h2)

    def test_eq_same_content(self):
        h1 = _hamt.new()
        h1 = _hamt.assoc(h1, 'a', 1)
        h1 = _hamt.assoc(h1, 'b', 2)

        h2 = _hamt.new()
        h2 = _hamt.assoc(h2, 'a', 1)
        h2 = _hamt.assoc(h2, 'b', 2)

        assert _hamt.eq(h1, h2)

    def test_eq_different_content(self):
        h1 = _hamt.new()
        h1 = _hamt.assoc(h1, 'a', 1)

        h2 = _hamt.new()
        h2 = _hamt.assoc(h2, 'a', 2)

        assert not _hamt.eq(h1, h2)

    def test_eq_different_keys(self):
        h1 = _hamt.new()
        h1 = _hamt.assoc(h1, 'a', 1)

        h2 = _hamt.new()
        h2 = _hamt.assoc(h2, 'b', 1)

        assert not _hamt.eq(h1, h2)

    def test_eq_different_length(self):
        h1 = _hamt.new()
        h1 = _hamt.assoc(h1, 'a', 1)

        h2 = _hamt.new()

        assert not _hamt.eq(h1, h2)


class TestHamtLen:
    def test_len_empty(self):
        h = _hamt.new()
        assert _hamt.len(h) == 0

    def test_len_after_assoc(self):
        h = _hamt.new()
        assert _hamt.len(h) == 0

        h = _hamt.assoc(h, 'a', 1)
        assert _hamt.len(h) == 1

        h = _hamt.assoc(h, 'b', 2)
        assert _hamt.len(h) == 2

    def test_len_after_without(self):
        h = _hamt.new()
        h = _hamt.assoc(h, 'a', 1)
        h = _hamt.assoc(h, 'b', 2)
        assert _hamt.len(h) == 2

        h = _hamt.without(h, 'a')
        assert _hamt.len(h) == 1


class TestHamtIterators:
    def test_iter_keys_empty(self):
        h = _hamt.new()
        keys = list(_hamt.iter_keys(h))
        assert keys == []

    def test_iter_keys(self):
        h = _hamt.new()
        h = _hamt.assoc(h, 'a', 1)
        h = _hamt.assoc(h, 'b', 2)
        h = _hamt.assoc(h, 'c', 3)

        keys = set(_hamt.iter_keys(h))
        assert keys == {'a', 'b', 'c'}

    def test_iter_values_empty(self):
        h = _hamt.new()
        values = list(_hamt.iter_values(h))
        assert values == []

    def test_iter_values(self):
        h = _hamt.new()
        h = _hamt.assoc(h, 'a', 1)
        h = _hamt.assoc(h, 'b', 2)
        h = _hamt.assoc(h, 'c', 3)

        values = set(_hamt.iter_values(h))
        assert values == {1, 2, 3}

    def test_iter_items_empty(self):
        h = _hamt.new()
        items = list(_hamt.iter_items(h))
        assert items == []

    def test_iter_items(self):
        h = _hamt.new()
        h = _hamt.assoc(h, 'a', 1)
        h = _hamt.assoc(h, 'b', 2)
        h = _hamt.assoc(h, 'c', 3)

        items = set(_hamt.iter_items(h))
        assert items == {('a', 1), ('b', 2), ('c', 3)}


class TestHamtTypeChecking:
    def test_assoc_type_error(self):
        with pytest.raises(TypeError, match='first argument must be a HAMT object'):
            _hamt.assoc({}, 'key', 'value')

    def test_without_type_error(self):
        with pytest.raises(TypeError, match='first argument must be a HAMT object'):
            _hamt.without({}, 'key')

    def test_find_type_error(self):
        with pytest.raises(TypeError, match='first argument must be a HAMT object'):
            _hamt.find({}, 'key')

    def test_eq_type_error_first(self):
        h = _hamt.new()
        with pytest.raises(TypeError, match='first argument must be a HAMT object'):
            _hamt.eq({}, h)

    def test_eq_type_error_second(self):
        h = _hamt.new()
        with pytest.raises(TypeError, match='second argument must be a HAMT object'):
            _hamt.eq(h, {})

    def test_len_type_error(self):
        with pytest.raises(TypeError, match='argument must be a HAMT object'):
            _hamt.len({})

    def test_iter_keys_type_error(self):
        with pytest.raises(TypeError, match='argument must be a HAMT object'):
            _hamt.iter_keys({})

    def test_iter_values_type_error(self):
        with pytest.raises(TypeError, match='argument must be a HAMT object'):
            _hamt.iter_values({})

    def test_iter_items_type_error(self):
        with pytest.raises(TypeError, match='argument must be a HAMT object'):
            _hamt.iter_items({})


class TestHamtImmutability:
    def test_assoc_does_not_modify_original(self):
        h1 = _hamt.new()
        h1 = _hamt.assoc(h1, 'a', 1)

        h2 = _hamt.assoc(h1, 'b', 2)

        assert _hamt.len(h1) == 1
        assert _hamt.find(h1, 'a') == 1
        assert _hamt.find(h1, 'b') is None

        assert _hamt.len(h2) == 2
        assert _hamt.find(h2, 'a') == 1
        assert _hamt.find(h2, 'b') == 2

    def test_without_does_not_modify_original(self):
        h1 = _hamt.new()
        h1 = _hamt.assoc(h1, 'a', 1)
        h1 = _hamt.assoc(h1, 'b', 2)

        h2 = _hamt.without(h1, 'a')

        assert _hamt.len(h1) == 2
        assert _hamt.find(h1, 'a') == 1
        assert _hamt.find(h1, 'b') == 2

        assert _hamt.len(h2) == 1
        assert _hamt.find(h2, 'a') is None
        assert _hamt.find(h2, 'b') == 2


class TestHamtLargeDataset:
    def test_many_items(self):
        h = _hamt.new()
        n = 1000

        # Add many items
        for i in range(n):
            h = _hamt.assoc(h, f'key_{i}', i)

        assert _hamt.len(h) == n

        # Verify all items
        for i in range(n):
            assert _hamt.find(h, f'key_{i}') == i

        # Remove half
        for i in range(0, n, 2):
            h = _hamt.without(h, f'key_{i}')

        assert _hamt.len(h) == n // 2

        # Verify remaining items
        for i in range(n):
            if i % 2 == 0:
                assert _hamt.find(h, f'key_{i}') is None
            else:
                assert _hamt.find(h, f'key_{i}') == i

    def test_iteration_large(self):
        h = _hamt.new()
        n = 100

        for i in range(n):
            h = _hamt.assoc(h, i, i * 2)

        keys = set(_hamt.iter_keys(h))
        values = set(_hamt.iter_values(h))
        items = set(_hamt.iter_items(h))

        assert len(keys) == n
        assert keys == set(range(n))
        assert values == set(i * 2 for i in range(n))
        assert items == set((i, i * 2) for i in range(n))
