import math

import pytest

from ..capture import ImportCaptureErrors
from ..proxy import _ProxyImporter
from ..proxy import proxy_import


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
