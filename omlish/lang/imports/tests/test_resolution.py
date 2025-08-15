import sys

from ..resolution import can_import


def test_can_import():
    mod = __package__ + '.foo'
    assert mod not in sys.modules
    assert can_import(mod)
    assert not can_import(mod + 'x')
    assert can_import('.foo', __package__)
    assert not can_import('.foox', __package__)
    assert mod not in sys.modules
