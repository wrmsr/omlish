import asyncio
import inspect
import typing as ta

import pytest
import sniffio

from ...lite.maysyncs import run_maysync
from ..imports.lazy import proxy_import
from ..maysyncs import make_maysync


if ta.TYPE_CHECKING:
    import trio
else:
    trio = proxy_import('trio')


##


def s_inc(i: int) -> int:
    return i + 1


async def a_inc(i: int) -> int:
    if (cal := sniffio.current_async_library()) == 'asyncio':
        await asyncio.sleep(.01)
    elif cal == 'trio':
        await trio.sleep(.01)
    else:
        raise RuntimeError(cal)
    return i + 2


m_inc = make_maysync(s_inc, a_inc)


async def m_frob(i: int) -> int:
    return await m_inc(i)


async def m_grob(i: int) -> int:
    return await m_frob(i + 10) + 100


def test_maysync():
    assert run_maysync(m_frob(3)) == 4
    assert run_maysync(m_grob(3)) == 114


@pytest.mark.asyncs('asyncio')
async def test_async_maysync():
    assert await m_frob(3) == 5
    assert await m_grob(3) == 115


##


async def a_foo():
    for i in range(3):
        yield s_inc(i)


async def a_bar(c=0):
    async for i in a_foo():
        c += i + 1
    return c


@pytest.mark.asyncs('asyncio')
async def test_async_generator():
    assert await a_bar(3) == 12


##


def s_fp_gen() -> ta.Generator[int]:
    yield 41
    yield s_inc(42)


async def a_fp_gen() -> ta.AsyncGenerator[int]:
    yield 41
    yield await a_inc(42)


m_fp_gen = make_maysync(s_fp_gen, a_fp_gen)


async def m_foo():
    for i in range(3):
        yield await m_inc(i)
    async for i in m_fp_gen():
        yield i


async def m_bar():
    c = 0
    async for i in m_foo():
        c += i + 1
    return c


async def m_bar_with_m_bar_s():
    assert run_maysync(m_bar()) == 95
    c = 0
    async for i in m_foo():
        c += i + 1
    return c


def test_sync_maysync_generator():
    assert run_maysync(m_bar()) == 95
    assert run_maysync(m_bar_with_m_bar_s()) == 95


@pytest.mark.asyncs('asyncio', 'trio')
async def test_async_maysync_generator():
    assert await m_bar() == 99
    assert await m_bar_with_m_bar_s() == 99


def test_inspect():
    assert inspect.iscoroutinefunction(m_fp_gen.__call__)  # type: ignore
