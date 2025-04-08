import pytest

from ..mappings import MappingFullKv
from ..unmodifiable_ import unmodifiable


def test_filtered():
    d = {i: i for i in range(20)}
    kv0 = MappingFullKv(d)
    assert kv0[1] == 1
    assert kv0[2] == 2
    kv0[2] = 3
    assert kv0[2] == 3

    kv1 = unmodifiable(kv0)
    assert kv1[2] == 2
    assert kv1[2] == 3
    with pytest.raises(TypeError):  # Noqa
        kv0[2] = 4
