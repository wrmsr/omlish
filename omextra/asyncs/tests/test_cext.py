import contextlib

import pytest


def test_cext():
    try:
        from .. import _asyncs  # type: ignore  # noqa
    except ImportError:
        pytest.skip('C extension not available')
    sync_await = _asyncs.sync_await

    c = 0

    def inc():
        nonlocal c
        c += 1
        return c

    #

    async def f1():
        return inc()

    assert sync_await(f1()) == 1

    async def f2():
        await f1()
        return inc()

    assert sync_await(f2()) == 3

    #

    @contextlib.asynccontextmanager
    async def acm():
        await f1()
        try:
            yield
        finally:
            await f1()

    async def f3():
        async with acm():
            return inc()

    assert sync_await(f3()) == 5
    assert c == 6

    #

    async def ag():
        try:
            await f2()
            yield inc()
            await f2()
            yield inc()
            await f2()
        finally:
            await f2()

    async def ai(exc=None):
        l = []
        async for i in ag():
            l.append(i)
            if exc is not None:
                raise exc(l)
        return l

    assert sync_await(ai()) == [9, 12]
    assert c == 16

    #

    class FooError(Exception):
        pass

    with pytest.raises(FooError) as ex:
        sync_await(ai(FooError))

    assert ex.value.args[0] == [19]
    assert c == 21
