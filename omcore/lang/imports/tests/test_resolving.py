import sys

import pytest

from ..resolving import can_import
from ..resolving import try_import


def test_can_import():
    mod = __package__ + '.foo1'
    assert mod not in sys.modules
    assert can_import(mod)
    assert not can_import(mod + 'x')
    assert can_import('.foo1', __package__)
    assert not can_import('.foox', __package__)
    assert mod not in sys.modules


def test_try_import():
    assert try_import('json') is sys.modules['json']
    assert try_import('zzznotamodule') is None

    # Dotted names return the leaf module, not the top-level package.
    assert try_import('os.path') is sys.modules['os'].path


def test_try_import_relative():
    from . import foo1

    assert try_import('.foo1', __package__) is foo1
    assert try_import('..tests.foo1', __package__) is foo1
    assert try_import('.foox', __package__) is None

    # Relative names require a package to resolve against - they must not silently resolve against anything else.
    with pytest.raises(TypeError):
        try_import('.foo1')
