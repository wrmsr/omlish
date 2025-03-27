import pytest

from ..base import Kv
from ..filtered import KeyFilteredMutableKv
from ..mappings import MappingKv
from ..mappings import MappingMutableKv
from ..transformed import KeyTransformedKv
from ..wrappers import underlying


def test_transformed():
    d = {i: i for i in range(20)}
    kv0 = MappingKv(d)
    assert kv0[1] == 1

    kv1: Kv[int, int] = KeyTransformedKv(kv0, t_to_f=lambda i: i * 2)
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
