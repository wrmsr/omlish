import typing as ta

import pytest

from ..generators import GeneratorLike_
from ..generators import adapt_generator_like
from ..generators import autostart
from ..generators import capture_coroutine
from ..generators import capture_generator
from ..generators import genmap
from ..generators import nextgen


def test_generator():
    def test():
        yield 1
        yield 2
        return 3
    gen = capture_generator(test())
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

    gen = capture_generator(test())

    assert next(gen) is None
    assert gen.send(1) == 2

    assert next(gen) is None
    assert gen.send(3) == 5

    with pytest.raises(StopIteration):
        next(gen)

    assert gen.value == 6


def test_capture_coroutine():
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

    with capture_coroutine(foo(3)) as g:
        g.send()
        assert g.send(2) == capture_coroutine.Yield(4)
        assert g.send(3) == capture_coroutine.Yield(6)
        assert g.send(4) == capture_coroutine.Yield(8)
        assert g.send(5) == capture_coroutine.Return(14)


def test_generator_like():
    class Foo(GeneratorLike_[int, int, int]):
        def __init__(self, n: int) -> None:
            super().__init__()
            self._n = n
            self._c = 0

        def send(self, x: int) -> int:
            self._c += x
            if self._n < 1:
                raise StopIteration(self._c)
            self._n -= 1
            return x * 2

    g = nextgen(adapt_generator_like(Foo(3)))
    assert g.send(2) == 4
    assert g.send(3) == 6
    assert g.send(4) == 8
    try:
        g.send(5)
    except StopIteration as e:
        assert e.value == 14  # noqa
    else:
        assert False  # noqa


def test_genmap():
    @autostart
    def f():
        i = yield
        while True:
            if i == 42:
                return '!'
            i = yield i + 1

    it = genmap(f(), range(3))
    assert list(it) == [1, 2, 3]
    assert not it.value.present

    it = genmap(f(), range(40, 50))
    assert list(it) == [41, 42]
    assert it.value.must() == '!'
