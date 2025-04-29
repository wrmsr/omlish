import operator

from ... import lang
from ...lite.strings import snake_case
from .. import pipes as fp


def test_fnpipes():
    assert fp.bind(operator.add, 1)(2) == 3

    assert (
        fp.bind(operator.add, 1)
        .pipe(operator.mul, 2)
    )(2) == 6

    assert (
        fp.bind(operator.add, 1)
        .apply(print)
        .pipe(operator.mul, 2)
        .apply(print)
    )(2) == 6

    assert (
        fp.bind(operator.add, 1)
        & print
        | fp.bind(operator.mul, 2)
        & print
    )(2) == 6

    assert fp.bind(operator.truediv, 2)(4) == .5
    assert fp.bind(operator.truediv, ..., 2)(4) == 2.

    #

    fn = fp.bind(lang.strip_suffix, ..., 'Action') | snake_case | fp.bind(str.replace, ..., '_', '-')
    assert fn('FooBarAction') == 'foo-bar'

    fn = fp.bind(lang.strip_suffix, ..., 'Action') | snake_case | fp.bind(str.replace, ..., '_', '-')
    assert fn('FooBarAction') == 'foo-bar'

    #

    l: list = []

    assert (
        (lambda x: x + 1)
        & fp.bind(l.append)
    )(5) == 6

    assert l == [6]
