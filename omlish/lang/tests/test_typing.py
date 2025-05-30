import typing as ta

from ..typing import copy_type
from ..typing import static_check_isinstance
from ..typing import static_check_issubclass
from ..typing import typed_lambda
from ..typing import typed_partial


##


def test_tl():
    l = typed_lambda(x=int, y=int)(lambda x, y: x + y)
    assert l(x=3, y=4) == 7
    assert ta.get_type_hints(l) == {'x': int, 'y': int}

    p = typed_partial(l, x=5)
    assert p(y=4) == 9
    assert ta.get_type_hints(p) == {'y': int}


def test_copy_type():
    def foo(i: int, s: str) -> float:
        return 0.

    @copy_type(foo)
    def foo2(*args, **kwargs):
        return 0.

    r = foo2(1, 's')
    if not isinstance(r, float):
        ta.assert_never(r)


##


static_check_isinstance[list]([])
static_check_isinstance[ta.Sequence]([])
# static_check_isinstance[ta.Sequence]({})  # FAILS

static_check_issubclass[list](list)
static_check_issubclass[ta.Sequence](list)
# static_check_issubclass[ta.Sequence](dict)  # FAILS


class Foo:
    pass


@static_check_issubclass[Foo]()
class Bar(Foo):
    pass


def test_bar():
    assert isinstance(Bar(), Bar)


# @static_check_issubclass[Foo]()  # FAILS
# class Baz:
#     pass
