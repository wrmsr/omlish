import typing as ta

from .... import lang
from .helpers import buffer_generator_writer


def test_bgw():
    def f():
        for _ in range(3):
            s = yield
            yield s + '?'
            yield s + '!'

    g = f()
    for s in 'abc':
        next(g)
        print(g.send(s))
        print(next(g))

    bg: ta.Any = lang.nextgen(buffer_generator_writer(lang.nextgen(f())))
    for s in 'abc':
        print(bg.send(s))

    bg = lang.nextgen(buffer_generator_writer(lang.nextgen(f()), terminator=lang.just('c?')))
    for s in 'abc':
        print(bg.send(s))
