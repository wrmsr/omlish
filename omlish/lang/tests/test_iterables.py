import typing as ta

import pytest

from ..iterables import Generator
from ..iterables import corogen
from ..iterables import itergen
from ..iterables import peek
from ..iterables import prodrange


def test_peek():
    it = range(4)
    v, it = peek(it)  # type: ignore
    assert v == 0
    assert list(it) == [0, 1, 2, 3]


def test_prodrange():
    assert list(prodrange(3, (0, 2))) == [
        (0, 0),
        (0, 1),
        (1, 0),
        (1, 1),
        (2, 0),
        (2, 1),
    ]


def test_itergen():
    l = list(reversed(range(3)))

    a = enumerate(l)
    assert list(a) == [(0, 2), (1, 1), (2, 0)]
    assert list(a) == []

    b = itergen(lambda: enumerate(l))
    for _ in range(2):
        assert list(b) == [(0, 2), (1, 1), (2, 0)]


def test_generator():
    def test():
        yield 1
        yield 2
        return 3
    gen = Generator(test())
    l = list(gen)
    assert l == [1, 2]
    assert gen.value == 3


def test_generator_send():
    def test():
        x = yield
        foo = yield x + 1
        assert foo is None

        x = yield
        foo = yield x + 2
        assert foo is None

        return x + 3

    gen = Generator(test())

    assert next(gen) is None
    assert gen.send(1) == 2

    assert next(gen) is None
    assert gen.send(3) == 5

    with pytest.raises(StopIteration):
        next(gen)

    assert gen.value == 6


def test_corogen():
    def foo(n: int) -> ta.Generator[int, int, int]:
        c = 0
        x = yield  # type: ignore
        for _ in range(n):
            c += x
            x = yield x * 2
        return c + x

    #

    # g = foo(3)
    # next(g)
    # assert g.send(2) == 4
    # assert g.send(3) == 6
    # assert g.send(4) == 8
    # try:
    #     g.send(5)
    # except StopIteration as e:
    #     assert e.value == 14  # noqa
    # else:
    #     raise RuntimeError

    #

    with corogen(foo(3)) as g:
        g.send()
        assert g.send(2) == corogen.Yield(4)
        assert g.send(3) == corogen.Yield(6)
        assert g.send(4) == corogen.Yield(8)
        assert g.send(5) == corogen.Return(14)
