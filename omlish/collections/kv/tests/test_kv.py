import typing as ta

import pytest

from ..base import Kv
from ..capabilities import Closeable
from ..capabilities import closing
from ..filtered import KeyFilteredMutableKv
from ..mappings import MappingKv
from ..mappings import MappingMutableKv
from ..transformed import KeyTransformedKv
from ..transformed import ValueTransformedKv
from ..wrappers import underlying


def test_transformed():
    d = {i: i for i in range(20)}
    kv0 = MappingKv(d)
    assert kv0[1] == 1

    kv1: Kv[int, int] = KeyTransformedKv(kv0, a_to_b=lambda i: i * 2)
    assert kv1[1] == 2
    print(list(underlying(kv1)))


def test_filtered():
    d = {i: i for i in range(20)}
    kv0 = MappingMutableKv(d)
    assert kv0[1] == 1
    assert kv0[2] == 2

    kv1 = KeyFilteredMutableKv(kv0, lambda i: i % 2 == 0)
    with pytest.raises(KeyError):
        kv1[1]  # noqa
    assert kv1[2] == 2

    del kv1[2]
    with pytest.raises(KeyError):
        kv1[2]  # noqa


class DummyCloseableKv(Kv[int, int], Closeable):
    closed = False

    def close(self) -> None:
        self.closed = True

    def __getitem__(self, k: int, /) -> int:
        if k == 0:
            return 1
        raise KeyError(k)

    def __len__(self) -> int:
        return 1

    def items(self) -> ta.Iterator[tuple[int, int]]:
        return iter([(0, 1)])


def test_closing():
    with closing(DummyCloseableKv()) as kv0:
        assert kv0[0] == 1
        assert not kv0.closed
    assert kv0.closed


def test_closing_wrapped():
    kv0 = DummyCloseableKv()
    kv1: Kv[int, int] = KeyTransformedKv(kv0, a_to_b=lambda k: k - 1)
    with closing(kv1):
        assert kv1[1] == 1
        assert not kv0.closed
    assert kv0.closed


def test_closing_wrapped2():
    kv0 = DummyCloseableKv()
    kv1: Kv[int, int] = KeyTransformedKv(kv0, a_to_b=lambda k: k - 1)
    with closing(ValueTransformedKv(kv1, b_to_a=lambda v: v + 1)) as kv2:
        assert kv2[1] == 2
        assert not kv0.closed
    assert kv0.closed
