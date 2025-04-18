import pytest

from ..filtered import filter_keys
from ..mappings import MutableMappingKv


def test_filtered():
    d = {i: i for i in range(20)}
    kv0 = MutableMappingKv(d)
    assert kv0[1] == 1
    assert kv0[2] == 2

    kv1 = filter_keys(lambda i: i % 2 == 0)(kv0)
    with pytest.raises(KeyError):
        kv1[1]  # noqa
    assert kv1[2] == 2

    del kv1[2]
    with pytest.raises(KeyError):
        kv1[2]  # noqa
