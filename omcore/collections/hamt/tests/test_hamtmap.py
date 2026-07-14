import typing as ta

import pytest

from ..hamtmap import HamtMap


try:
    from .. import _hamt  # type: ignore  # noqa
except ImportError:
    pytest.skip('_hamt module not built', allow_module_level=True)


def items_dict(m: HamtMap[ta.Any, ta.Any]) -> dict[ta.Any, ta.Any]:
    return dict(m.items())


class CollisionKey:
    def __init__(self, value: int) -> None:
        self.value = value

    def __hash__(self) -> int:
        return 42

    def __eq__(self, other: object) -> bool:
        return isinstance(other, CollisionKey) and self.value == other.value

    def __repr__(self) -> str:
        return f'CollisionKey({self.value!r})'


def test_empty_map_basics() -> None:
    m: HamtMap[int, str] = HamtMap()

    assert len(m) == 0
    assert list(m) == []
    assert list(m.items()) == []
    assert 1 not in m

    with pytest.raises(KeyError):
        _ = m[1]


def test_with_getitem_contains_len() -> None:
    m: HamtMap[int, str] = HamtMap()

    m = m.with_(1, 'a')
    m = m.with_(2, 'b')
    m = m.with_(3, 'c')

    assert len(m) == 3
    assert 1 in m
    assert 2 in m
    assert 3 in m
    assert 4 not in m

    assert m[1] == 'a'
    assert m[2] == 'b'
    assert m[3] == 'c'


def test_iter_and_items_match_contents() -> None:
    m: HamtMap[int, str] = HamtMap()
    for k, v in [(10, 'x'), (20, 'y'), (30, 'z')]:
        m = m.with_(k, v)

    assert set(m) == {10, 20, 30}
    assert set(m.items()) == {(10, 'x'), (20, 'y'), (30, 'z')}
    assert items_dict(m) == {10: 'x', 20: 'y', 30: 'z'}


def test_with_overwrites_existing_key() -> None:
    m0: HamtMap[int, str] = HamtMap()
    m1 = m0.with_(1, 'a')
    m2 = m1.with_(1, 'updated')

    assert len(m1) == 1
    assert len(m2) == 1

    assert m1[1] == 'a'
    assert m2[1] == 'updated'

    assert items_dict(m1) == {1: 'a'}
    assert items_dict(m2) == {1: 'updated'}


def test_without_present_key() -> None:
    m: HamtMap[int, str] = HamtMap()
    m = m.with_(1, 'a').with_(2, 'b').with_(3, 'c')

    m2 = m.without(2)

    assert len(m2) == 2
    assert 2 not in m2
    assert items_dict(m2) == {1: 'a', 3: 'c'}

    with pytest.raises(KeyError):
        _ = m2[2]


def test_without_missing_key_returns_same_object() -> None:
    m: HamtMap[int, str] = HamtMap()
    m = m.with_(1, 'a').with_(2, 'b')

    m2 = m.without(999)

    assert m2 is m
    assert len(m2) == 2
    assert items_dict(m2) == {1: 'a', 2: 'b'}


def test_persistence_old_versions_unchanged() -> None:
    m0: HamtMap[int, str] = HamtMap()
    m1 = m0.with_(1, 'a')
    m2 = m1.with_(2, 'b')
    m3 = m2.without(1)

    assert len(m0) == 0
    assert items_dict(m0) == {}

    assert items_dict(m1) == {1: 'a'}
    assert items_dict(m2) == {1: 'a', 2: 'b'}
    assert items_dict(m3) == {2: 'b'}


def test_default_inserts_only_when_missing() -> None:
    m0: HamtMap[int, str] = HamtMap()

    m1 = m0.default(1, 'a')
    m2 = m1.default(1, 'new')

    assert isinstance(m1, HamtMap)
    assert isinstance(m2, HamtMap)

    assert items_dict(m1) == {1: 'a'}
    assert items_dict(m2) == {1: 'a'}

    assert m1[1] == 'a'
    assert m2[1] == 'a'


def test_default_does_not_change_existing_mapping() -> None:
    m0: HamtMap[int, str] = HamtMap()
    m1 = m0.with_(1, 'a')

    m2 = m1.default(1, 'ignored')

    assert isinstance(m2, HamtMap)
    assert items_dict(m1) == {1: 'a'}
    assert items_dict(m2) == {1: 'a'}
    assert m2[1] == 'a'


def test_collision_keys_work() -> None:
    k1 = CollisionKey(1)
    k2 = CollisionKey(2)
    k3 = CollisionKey(3)

    m: HamtMap[CollisionKey, str] = HamtMap()
    m = m.with_(k1, 'a')
    m = m.with_(k2, 'b')
    m = m.with_(k3, 'c')

    assert len(m) == 3
    assert k1 in m
    assert k2 in m
    assert k3 in m

    assert m[k1] == 'a'
    assert m[k2] == 'b'
    assert m[k3] == 'c'

    got = items_dict(m)
    assert got == {k1: 'a', k2: 'b', k3: 'c'}


def test_collision_key_overwrite() -> None:
    k1a = CollisionKey(1)
    k1b = CollisionKey(1)

    m: HamtMap[CollisionKey, str] = HamtMap()
    m = m.with_(k1a, 'a')
    m2 = m.with_(k1b, 'updated')

    assert len(m) == 1
    assert len(m2) == 1

    assert m[k1a] == 'a'
    assert m2[k1a] == 'updated'
    assert m2[k1b] == 'updated'


def test_collision_key_delete() -> None:
    ks = [CollisionKey(i) for i in range(5)]

    m: HamtMap[CollisionKey, str] = HamtMap()
    for i, k in enumerate(ks):
        m = m.with_(k, f'v{i}')

    m2 = m.without(ks[2])

    assert len(m2) == 4
    assert ks[2] not in m2

    for i, k in enumerate(ks):
        if i == 2:
            with pytest.raises(KeyError):
                _ = m2[k]
        else:
            assert m2[k] == f'v{i}'


def test_randomized_against_builtin_dict() -> None:
    m: HamtMap[int, str] = HamtMap()
    d: dict[int, str] = {}

    # deterministic pseudo-random sequence without importing random
    for i in range(500):
        k = (i * 37) % 53
        op = i % 4
        v = f'v{i}'

        if op in (0, 1):
            m = m.with_(k, v)
            d[k] = v

        elif op == 2:
            m = m.without(k)
            d.pop(k, None)

        else:
            if k in d:
                assert k in m
                assert m[k] == d[k]
            else:
                assert k not in m
                with pytest.raises(KeyError):
                    _ = m[k]

        assert len(m) == len(d)
        assert set(m) == set(d.keys())
        assert items_dict(m) == d


def test_many_versions_remain_valid() -> None:
    versions: list[HamtMap[int, str]] = [HamtMap()]

    m: HamtMap[int, str] = HamtMap()
    for i in range(20):
        m = m.with_(i, f'v{i}')
        versions.append(m)

    for i in range(20):
        m = m.without(i)
        versions.append(m)

    for ver in versions:
        got = items_dict(ver)
        assert len(ver) == len(got)
        assert set(ver) == set(got.keys())

        for k, v in got.items():
            assert k in ver
            assert ver[k] == v


def test_with_rejects_none_values_if_that_is_intended_api() -> None:
    m: HamtMap[int, str | None] = HamtMap()

    with pytest.raises(ValueError):  # noqa
        m.with_(1, None)
