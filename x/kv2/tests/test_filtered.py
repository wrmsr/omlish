import pytest

from ..filtered import KeyFilteredKv
from ..mappings import MappingFullKv
from ..shrinkwraps import shrinkwrap_factory


def test_filtered():
    d = {i: i for i in range(20)}
    kv0 = MappingFullKv(d)
    assert kv0[1] == 1
    assert kv0[2] == 2

    kv1 = shrinkwrap_factory(KeyFilteredKv)(kv0, lambda i: i % 2 == 0)
    with pytest.raises(KeyError):
        kv1[1]  # noqa
    assert kv1[2] == 2

    del kv1[2]
    with pytest.raises(KeyError):
        kv1[2]  # noqa
