import math
import sys

import pytest

from ..capture import ImportCaptureErrors
from ..proxy import _ProxyImporter
from ..proxy import proxy_import
from ..proxy import proxy_init


def test_proxy():
    sys = proxy_import('sys')
    assert sys.version_info[0] == 3


def test_proxy_importer_module_tree():
    pi = _ProxyImporter()
    with pi._lock:  # noqa
        c = pi._get_or_make_module_locked('a.b.c')  # noqa
        a = pi._modules_by_name['a']  # noqa
        b = pi._modules_by_name['a.b']  # noqa

    assert c.parent is b
    assert b.parent is a
    assert a.parent is None
    assert c.root is a
    assert b.root is a
    assert a.root is a
    assert a.descendants == {b, c}
    assert not b.descendants


def test_capture_foreign_attr_error():
    with pytest.raises(ImportCaptureErrors.AttrError):
        from . import badcapture  # noqa


def test_proxy_init_aliased_attrs():
    from . import aliasinit  # noqa

    assert 'alias' not in aliasinit.__dict__
    assert aliasinit.alias.MARKER == 420  # type: ignore[attr-defined]
    assert 'alias' in aliasinit.__dict__  # cached by LazyGlobals

    assert aliasinit.m2.MARKER2 == 421  # type: ignore[attr-defined]


def test_proxy_init_dotted_spec():
    glo: dict = {'__name__': 'fakemod', '__package__': ''}
    proxy_init(glo, 'importlib.resources.abc')

    assert 'abc' not in glo
    v = glo['__getattr__']('abc')

    import importlib.resources.abc
    assert v is importlib.resources.abc


def test_proxy_init_multi_dot_relative_spec():
    glo: dict = {'__name__': 'fakemod2', '__package__': 'omcore.lang'}
    proxy_init(glo, '..lang.maybes')

    assert 'maybes' not in glo
    v = glo['__getattr__']('maybes')

    from ... import maybes
    assert v is maybes


def test_auto_proxy_import_eager():
    sys.modules.pop('colorsys', None)

    from . import eagerimp  # noqa

    assert 'colorsys' in sys.modules
    assert eagerimp.colorsys.hsv_to_rgb is sys.modules['colorsys'].hsv_to_rgb


def test_auto_proxy_init():
    from . import foo2  # noqa

    for k in [
        'math',
        'qux',
        'abc',
        'ghi',
        'math2',
        'qux2',
        'jkl2',
        'jarf2',
        'karf',
        'pi',
        # 'delete_me',
    ]:
        assert k not in foo2.__dict__

    assert foo2.math.pi is math.pi
    assert foo2.qux.jarf == 420
    assert foo2.ghi == 2
    assert not hasattr(foo2, 'jkl')
    assert foo2.math2.pi is math.pi
    assert foo2.qux2.jarf == 420
    assert foo2.jkl2 == 421
    assert foo2.jarf2 == 420
    assert foo2.karf == 520
    assert foo2.pi is math.pi
    assert foo2.is_deep3 is True
    assert foo2.is_deep5 is True
    assert foo2.is_deep3a is True
    assert foo2.is_deep5a is True
    assert foo2.is_foo3_sub1 is True
    assert foo2.sub2.is_foo3_sub2 is True
    assert foo2.omcore.lang.imports.tests.foo2.deep1b.deep2b.deep3b.is_deep3b is True
    assert foo2.my_deep5b.is_deep5b is True  # noqa

    assert getattr(foo2, '_auto_proxy_init_unreferenced') == [foo2.__name__ + '.bar.baz.delete_me']
