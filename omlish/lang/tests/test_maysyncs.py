import asyncio

import pytest

from ..maysyncs import make_maysync
from ..maysyncs import maysync


##


def s_inc(i: int) -> int:
    return i + 1


async def a_inc(i: int) -> int:
    await asyncio.sleep(.01)
    return i + 2


m_inc = make_maysync(s_inc, a_inc)


@maysync
async def m_frob(i: int) -> int:
    return await m_inc(i).m()


@maysync
async def m_grob(i: int) -> int:
    return await m_frob(i + 10).m() + 100


def test_maysync():
    assert m_frob(3).s() == 4
    assert m_grob(3).s() == 114


@pytest.mark.asyncs('asyncio')
async def test_async_maysync():
    assert await m_frob(3).a() == 5
    assert await m_grob(3).a() == 115


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
    assert (await a_bar(3)) == 12


##


# @maysync
# async def m_foo():
#     for i in range(3):
#         yield await m_inc(i).m()
#
#
# @maysync
# async def m_bar():
#     c = 0
#     async for i in await m_foo().m():
#         c += i + 1
#     return c


# @pytest.mark.asyncs('asyncio')
# async def test_async_maysync_generator():
#     assert (await m_bar().a()) == 9
