import typing as ta

from ..typing import copy_type
from ..typing import typed_lambda
from ..typing import typed_partial


def test_tl():
    l = typed_lambda(x=int, y=int)(lambda x, y: x + y)
    assert l(x=3, y=4) == 7
    assert ta.get_type_hints(l) == {'x': int, 'y': int}

    p = typed_partial(l, x=5)
    assert p(y=4) == 9
    assert ta.get_type_hints(p) == {'y': int}


def test_copy_type():
    def foo(i: int, s: str) -> float:
        raise NotImplementedError

    @copy_type(foo)
    def foo2(*args, **kwargs):
        raise NotImplementedError

    r = foo2(1, 's')
    if not isinstance(r, float):
        ta.assert_never(r)
