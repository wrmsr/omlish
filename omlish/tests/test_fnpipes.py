import operator

from .. import fnpipes as fpi
from .. import lang


def test_fnpipes():
    assert fpi.bind(operator.add, 1)(2) == 3

    assert (
        fpi.bind(operator.add, 1)
        .pipe(operator.mul, 2)
    )(2) == 6

    assert (
        fpi.bind(operator.add, 1)
        .apply(print)
        .pipe(operator.mul, 2)
        .apply(print)
    )(2) == 6

    assert (
        fpi.bind(operator.add, 1)
        & print
        | fpi.bind(operator.mul, 2)
        & print
    )(2) == 6

    assert fpi.bind(operator.truediv, 2)(4) == .5
    assert fpi.bind(operator.truediv, ..., 2)(4) == 2.

    #

    fn = fpi.bind(lang.strip_suffix, ..., 'Action') | lang.snake_case | fpi.bind(str.replace, ..., '_', '-')
    assert fn('FooBarAction') == 'foo-bar'

    fn = fpi.bind(lang.strip_suffix, ..., 'Action') | lang.snake_case | fpi.bind(str.replace, ..., '_', '-')
    assert fn('FooBarAction') == 'foo-bar'
