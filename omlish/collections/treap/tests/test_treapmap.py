import random
import typing as ta

import pytest

from .. import treapmap as tm


def test_treapmap():
    m: tm.TreapMap[int, str] = tm.new_treap_map()

    for i in range(32):
        m = m.with_(i, str(i))

    m = m.with_(52, 'hello')
    m = m.with_(53, 'world')
    m = m.with_(52, 'Hello')
    m = m.with_(54, "I'm")
    m = m.with_(55, 'here')

    print(m)
    print('===')

    it = m.items()
    while it.has_next():
        print(it.next())
    print('===')

    assert len(m) == 36
    print('===')

    old = m.with_(500, 'five hundred')
    m = m.without(53)

    with pytest.raises(KeyError):
        print(m[53])
    print(old[53])
    print(old[52])
    print(old[500])
    print('===')

    it = m.items()
    while it.has_next():
        print(it.next())
    print('===')

    rit = m.items_desc()
    while rit.has_next():
        print(rit.next())
    print('===')

    it = m.items_from(30)
    while it.has_next():
        print(it.next())
    print('===')

    rit = m.items_from_desc(30)
    while rit.has_next():
        print(rit.next())
    print('===')


##


def new_map() -> tm.TreapMap[int, str]:
    return ta.cast('tm.TreapMap[int, str]', tm.new_treap_map())


def items_list(m: tm.TreapMap[int, str]) -> list[tuple[int, str]]:
    return list(m.items())


def items_desc_list(m: tm.TreapMap[int, str]) -> list[tuple[int, str]]:
    return list(m.items_desc())


def test_empty_map_basics():
    m = new_map()

    assert len(m) == 0
    assert list(m) == []
    assert items_list(m) == []
    assert items_desc_list(m) == []
    assert list(m.items_from(10)) == []
    assert list(m.items_from_desc(10)) == []
    assert 10 not in m

    with pytest.raises(KeyError):
        _ = m[10]


def test_with_and_getitem_and_contains():
    m = new_map()
    m = m.with_(2, 'b')
    m = m.with_(1, 'a')
    m = m.with_(3, 'c')

    assert len(m) == 3
    assert m[1] == 'a'
    assert m[2] == 'b'
    assert m[3] == 'c'

    assert 1 in m
    assert 2 in m
    assert 3 in m
    assert 99 not in m


def test_iter_yields_keys_in_sorted_order():
    m = new_map()
    for k, v in [(5, 'e'), (2, 'b'), (8, 'h'), (1, 'a'), (3, 'c')]:
        m = m.with_(k, v)

    assert list(m) == [1, 2, 3, 5, 8]


def test_items_and_items_desc():
    m = new_map()
    for k, v in [(5, 'e'), (2, 'b'), (8, 'h'), (1, 'a'), (3, 'c')]:
        m = m.with_(k, v)

    assert items_list(m) == [(1, 'a'), (2, 'b'), (3, 'c'), (5, 'e'), (8, 'h')]
    assert items_desc_list(m) == [(8, 'h'), (5, 'e'), (3, 'c'), (2, 'b'), (1, 'a')]


def test_items_iterator_protocol():
    m = new_map().with_(1, 'a').with_(2, 'b')

    it = m.items()
    assert iter(it) is it
    assert it.has_next() is True
    assert next(it) == (1, 'a')
    assert it.has_next() is True
    assert next(it) == (2, 'b')
    assert it.has_next() is False

    with pytest.raises(StopIteration):
        next(it)


def test_items_desc_iterator_protocol():
    m = new_map().with_(1, 'a').with_(2, 'b')

    it = m.items_desc()
    assert iter(it) is it
    assert it.has_next() is True
    assert next(it) == (2, 'b')
    assert it.has_next() is True
    assert next(it) == (1, 'a')
    assert it.has_next() is False

    with pytest.raises(StopIteration):
        next(it)


def test_items_from_exact_key():
    m = new_map()
    for k, v in [(10, 'j'), (20, 't'), (30, 'th'), (40, 'f')]:
        m = m.with_(k, v)

    assert list(m.items_from(20)) == [(20, 't'), (30, 'th'), (40, 'f')]


def test_items_from_between_keys():
    m = new_map()
    for k, v in [(10, 'j'), (20, 't'), (30, 'th'), (40, 'f')]:
        m = m.with_(k, v)

    assert list(m.items_from(25)) == [(30, 'th'), (40, 'f')]


def test_items_from_before_all():
    m = new_map()
    for k, v in [(10, 'j'), (20, 't'), (30, 'th')]:
        m = m.with_(k, v)

    assert list(m.items_from(0)) == [(10, 'j'), (20, 't'), (30, 'th')]


def test_items_from_after_all_is_empty():
    m = new_map()
    for k, v in [(10, 'j'), (20, 't'), (30, 'th')]:
        m = m.with_(k, v)

    assert list(m.items_from(99)) == []


def test_items_from_desc_exact_key():
    m = new_map()
    for k, v in [(10, 'j'), (20, 't'), (30, 'th'), (40, 'f')]:
        m = m.with_(k, v)

    assert list(m.items_from_desc(30)) == [(30, 'th'), (20, 't'), (10, 'j')]


def test_items_from_desc_between_keys():
    m = new_map()
    for k, v in [(10, 'j'), (20, 't'), (30, 'th'), (40, 'f')]:
        m = m.with_(k, v)

    assert list(m.items_from_desc(35)) == [(30, 'th'), (20, 't'), (10, 'j')]


def test_items_from_desc_after_all():
    m = new_map()
    for k, v in [(10, 'j'), (20, 't'), (30, 'th')]:
        m = m.with_(k, v)

    assert list(m.items_from_desc(99)) == [(30, 'th'), (20, 't'), (10, 'j')]


def test_items_from_desc_before_all_is_empty():
    m = new_map()
    for k, v in [(10, 'j'), (20, 't'), (30, 'th')]:
        m = m.with_(k, v)

    assert list(m.items_from_desc(0)) == []


def test_with_overwrites_existing_key():
    m0 = new_map()
    m1 = m0.with_(1, 'a')
    m2 = m1.with_(1, 'updated')

    assert len(m1) == 1
    assert len(m2) == 1
    assert m1[1] == 'a'
    assert m2[1] == 'updated'
    assert items_list(m2) == [(1, 'updated')]


def test_without_present():
    m = new_map()
    for k, v in [(1, 'a'), (2, 'b'), (3, 'c')]:
        m = m.with_(k, v)

    m2 = m.without(2)

    assert len(m2) == 2
    assert items_list(m2) == [(1, 'a'), (3, 'c')]
    with pytest.raises(KeyError):
        _ = m2[2]


def test_without_missing_is_noop_by_contents():
    m = new_map()
    for k, v in [(1, 'a'), (2, 'b')]:
        m = m.with_(k, v)

    m2 = m.without(999)

    assert len(m2) == len(m)
    assert items_list(m2) == items_list(m)


def test_default_inserts_only_when_missing():
    m0 = new_map()
    m1 = m0.default(1, 'a')
    m2 = m1.default(1, 'new')

    assert len(m1) == 1
    assert len(m2) == 1
    assert m1[1] == 'a'
    assert m2[1] == 'a'


def test_persistence_old_versions_unchanged():
    m0 = new_map()
    m1 = m0.with_(1, 'a')
    m2 = m1.with_(2, 'b')
    m3 = m2.without(1)

    assert items_list(m0) == []
    assert items_list(m1) == [(1, 'a')]
    assert items_list(m2) == [(1, 'a'), (2, 'b')]
    assert items_list(m3) == [(2, 'b')]


def test_len_tracks_unique_keys_not_updates():
    m = new_map()
    for i in range(10):
        m = m.with_(i, str(i))
    assert len(m) == 10

    for i in range(10):
        m = m.with_(i, f'x{i}')
    assert len(m) == 10


def test_randomized_against_builtin_dict():
    rng = random.Random(0xBEEF)

    m = new_map()
    d: dict[int, str] = {}

    for _ in range(500):
        op = rng.choice(['set', 'del', 'get', 'default'])
        k = rng.randrange(40)
        v = f'v{rng.randrange(1000)}'

        if op == 'set':
            m = m.with_(k, v)
            d[k] = v

        elif op == 'del':
            m = m.without(k)
            d.pop(k, None)

        elif op == 'default':
            old = dict(d)
            m2 = m.default(k, v)
            d.setdefault(k, v)
            assert items_list(m2) == sorted(d.items())
            if k in old:
                assert items_list(m2) == items_list(m)
            m = m2

        else:
            if k in d:
                assert m[k] == d[k]
                assert k in m
            else:
                with pytest.raises(KeyError):
                    _ = m[k]
                assert k not in m

        assert len(m) == len(d)
        assert list(m) == sorted(d.keys())
        assert items_list(m) == sorted(d.items())
        assert items_desc_list(m) == sorted(d.items(), reverse=True)


def test_randomized_items_from_agrees_with_sorted_dict():
    rng = random.Random(0x12345)

    m = new_map()
    d: dict[int, str] = {}

    for _ in range(100):
        k = rng.randrange(60)
        v = f'v{k}'
        m = m.with_(k, v)
        d[k] = v

    sorted_items = sorted(d.items())

    for probe in range(-5, 66):
        expect = [(k, v) for (k, v) in sorted_items if k >= probe]
        assert list(m.items_from(probe)) == expect

        expect_desc = [(k, v) for (k, v) in reversed(sorted_items) if k <= probe]
        assert list(m.items_from_desc(probe)) == expect_desc
