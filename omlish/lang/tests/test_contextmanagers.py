import contextlib
import typing as ta

import pytest

from ..contextmanagers import AsyncContextManager
from ..contextmanagers import ContextManager
from ..contextmanagers import ExitStacked
from ..contextmanagers import context_wrapped


def test_exit_stacked():
    class A(ExitStacked):
        pass

    with A() as a:
        assert isinstance(a, A)
        assert isinstance(a._exit_stack, contextlib.ExitStack)  # noqa

    class B(ExitStacked):

        def __enter__(self):
            return 'hi'

    with B() as b:
        assert b == 'hi'


def test_context_wrapped():
    class CM:
        count = 0

        def __enter__(self):
            self.count += 1

        def __exit__(self, et, e, tb):
            pass

    cm = CM()

    @context_wrapped(cm)
    def f(x):
        return x + 1

    assert f(4) == 5
    assert cm.count == 1
    assert f(5) == 6
    assert cm.count == 2

    class C:
        def __init__(self) -> None:
            self.cm = CM()

        @context_wrapped('cm')
        def f(self, x):
            return x + 2

    for _ in range(2):
        c = C()
        assert c.f(6) == 8
        assert c.cm.count == 1

    gcm = CM()

    @context_wrapped(lambda x: gcm)  # noqa
    def g(x):
        return x + 3

    assert g(10) == 13
    assert gcm.count == 1

    class D:
        @context_wrapped(lambda self, x: gcm)  # noqa
        def g(self, x):
            return x + 3

    d = D()
    assert d.g(10) == 13
    assert gcm.count == 2


def test_contextmanager_class():
    class C(ContextManager[int]):
        c = 0

        def __contextmanager__(self) -> ta.Iterable[int]:
            self.c += 1
            yield 420
            self.c += 1

    c = C()
    with c as n:
        assert n == 420
        assert c.c == 1
    assert c.c == 2


@pytest.mark.asyncs('asyncio')
async def test_asynccontextmanager_class():
    class C(AsyncContextManager[int]):
        c = 0

        async def __asynccontextmanager__(self) -> ta.AsyncIterator[int]:
            self.c += 1
            yield 420
            self.c += 1

    c = C()
    async with c as n:
        assert n == 420
        assert c.c == 1
    assert c.c == 2
