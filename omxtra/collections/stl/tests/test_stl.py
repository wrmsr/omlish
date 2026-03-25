import pytest


try:
    from .. import stl
except ImportError:
    pytest.skip('_stl module not built', allow_module_level=True)


def test_stl():
    m = stl.IntIntMap()
    m[1] = 2
    assert m[1] == 2
