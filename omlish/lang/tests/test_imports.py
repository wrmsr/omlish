import sys

from ..imports import can_import
from ..imports import lazy_import
from ..imports import proxy_import
from ..imports import yield_importable


def test_can_import():
    mod = __package__ + '.foo'
    assert mod not in sys.modules
    assert can_import(mod)
    assert not can_import(mod + 'x')
    assert can_import('.foo', __package__)
    assert not can_import('.foox', __package__)
    assert mod not in sys.modules


def test_lazy():
    sys = lazy_import('sys')
    assert sys().version_info[0] == 3


def test_proxy():
    sys = proxy_import('sys')
    assert sys.version_info[0] == 3


def test_yield_importable():
    base_pkg = __package__.rpartition('.')[0]

    lst = list(yield_importable(base_pkg))
    assert base_pkg + '.imports' in lst
    assert __name__ not in lst

    lst = list(yield_importable(base_pkg, recursive=True))
    assert base_pkg + '.imports' in lst
    assert __name__ in lst
