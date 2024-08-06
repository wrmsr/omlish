"""
See:
 - https://github.com/sqlalchemy/sqlalchemy/blob/3ac034057ce621379fb8e0926b851a903d2c7e0b/lib/sqlalchemy/util/concurrency.py
"""  # noqa
import sys
import types
import typing as ta

import anyio
import pytest

from ... import lang
from .. import asyncs


if ta.TYPE_CHECKING:
    import asyncio

    import greenlet
else:
    asyncio = lang.proxy_import('asyncio')

    greenlet = lang.proxy_import('greenlet')


##


def simple_s_to_a(fn):
    async def inner(*args, **kwargs):
        return fn(*args, **kwargs)
    return inner


def simple_a_to_s(fn):
    def inner(*args, **kwargs):
        return asyncs.sync_await(fn, *args, **kwargs)
    return inner


##
# https://gist.github.com/snaury/202bf4f22c41ca34e56297bae5f33fef

T = ta.TypeVar('T')


_BRIDGE_GREENLET_ATTR = f'__{__package__.replace(".", "__")}__bridge_greenlet__'


class AwaitRequiredError(Exception):
    pass


class MissingBridgeGreenletError(Exception):
    pass


def _safe_cancel_awaitable(awaitable: ta.Awaitable[ta.Any]) -> None:
    # https://docs.python.org/3/reference/datamodel.html#coroutine.close
    if asyncio.iscoroutine(awaitable):
        awaitable.close()  # noqa


def s_to_a_await(awaitable: ta.Awaitable[T]) -> T:
    g = greenlet.getcurrent()

    if not getattr(g, _BRIDGE_GREENLET_ATTR, False):
        _safe_cancel_awaitable(awaitable)
        raise MissingBridgeGreenletError

    return g.parent.switch(awaitable)


def s_to_a(fn, *, require_await=False):
    @types.coroutine
    def inner(*args, **kwargs):
        result: ta.Any
        g = greenlet.greenlet(fn)
        setattr(g, _BRIDGE_GREENLET_ATTR, True)
        switch_occurred = False

        result = g.switch(*args, **kwargs)
        while not g.dead:
            switch_occurred = True
            try:
                value = yield result
            except BaseException:  # noqa
                result = g.throw(*sys.exc_info())
            else:
                result = g.switch(value)

        if require_await and not switch_occurred:
            raise AwaitRequiredError

        return result

    return inner


def a_to_s(fn):
    def inner(*args, **kwargs):
        ret = missing = object()

        async def gate():
            nonlocal ret
            ret = await fn(*args, **kwargs)

        cr = gate()
        sv = None
        try:
            while True:
                try:  # noqa
                    sv = cr.send(sv)
                except StopIteration:
                    break

                if ret is missing or cr.cr_await is not None or cr.cr_running:
                    sv = s_to_a_await(sv)

        finally:
            cr.close()

        return ret

    return inner


##


def callback(arg):
    return f'callback({arg})'


async def a_callback(arg):
    return f'a_callback({arg})'


def func(cb, arg):
    return f'func({arg}) -> {cb(arg)}'


async def a_func(a_cb, arg):
    return f'a_func({arg}) -> {await a_cb(arg)}'


async def _test_async_bridge():
    assert (await a_func(a_callback, 'arg')) == 'a_func(arg) -> a_callback(arg)'
    assert (await a_func(s_to_a(callback), 'arg')) == 'a_func(arg) -> callback(arg)'

    assert (await s_to_a(func)(callback, 'arg')) == 'func(arg) -> callback(arg)'
    assert (await s_to_a(func)(a_to_s(a_callback), 'arg')) == 'func(arg) -> a_callback(arg)'


@pytest.mark.asyncio
async def test_async_bridge_asyncio():
    await _test_async_bridge()


@pytest.mark.trio
async def test_async_bridge_trio():
    await _test_async_bridge()


def test_bridge():
    assert func(callback, 'arg') == 'func(arg) -> callback(arg)'
    assert func(a_to_s(a_callback), 'arg') == 'func(arg) -> a_callback(arg)'

    assert a_to_s(a_func)(a_callback, 'arg') == 'a_func(arg) -> a_callback(arg)'
    assert a_to_s(a_func)(s_to_a(callback), 'arg') == 'a_func(arg) -> callback(arg)'


##


async def a_sleep_callback(arg):
    await anyio.sleep(.01)
    return f'a_sleep_callback({arg})'


async def _test_async_bridge2():
    await anyio.sleep(.01)
    assert (await s_to_a(func)(a_to_s(a_sleep_callback), 'arg')) == 'func(arg) -> a_sleep_callback(arg)'


@pytest.mark.asyncio
async def test_async_bridge2_asyncio():
    await _test_async_bridge2()


@pytest.mark.trio
async def test_async_bridge2_trio():
    await _test_async_bridge2()
