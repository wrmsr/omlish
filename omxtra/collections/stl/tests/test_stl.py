import typing as ta

import pytest


try:
    from .. import stl
except ImportError:
    pytest.skip('_stl module not built', allow_module_level=True)


def test_stl():
    m: ta.Any
    for cls, k, v, k2 in [
        (stl.IntIntMap, 1, 2, 3),
        (stl.IntObjectMap, 1, '2', 3),
        (stl.ObjectIntMap, '1', 2, '3'),
        (stl.ObjectObjectMap, '1', '2', '3'),
    ]:
        m = cls()
        m[k] = v
        assert m[k] == v
        with pytest.raises(KeyError):  # noqa
            m[k2]  # noqa
