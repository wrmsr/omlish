import math

from ..proxy import proxy_import


def test_proxy():
    sys = proxy_import('sys')
    assert sys.version_info[0] == 3


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

    assert getattr(foo2, '_auto_proxy_init_unreferenced') == [foo2.__name__ + '.bar.baz.delete_me']
