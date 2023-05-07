import typing as ta

from .. import typing as tu


def test_tl():
    l = tu.typed_lambda(x=int, y=int)(lambda x, y: x + y)
    assert l(x=3, y=4) == 7
    assert ta.get_type_hints(l) == {'x': int, 'y': int}

    p = tu.typed_partial(l, x=5)
    assert p(y=4) == 9
    assert ta.get_type_hints(p) == {'y': int}
