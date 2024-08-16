import pytest

from ..iterables import Generator
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
