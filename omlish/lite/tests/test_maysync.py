# ruff: noqa: UP043
import typing as ta
import unittest

from ..maysync import make_maysync
from ..maysync import run_maysync
from .utils import sync_async_list
from .utils import sync_await


##


def s_inc(i: int) -> int:
    return i + 1


async def a_inc(i: int) -> int:
    return i + 2


m_inc = make_maysync(s_inc, a_inc)


async def m_frob(i: int) -> int:
    return await m_inc(i + 10)


async def m_grob(i: int) -> int:
    return await m_frob(i + 20) + 100


class TestMaysync(unittest.TestCase):
    def test_maysync(self):
        assert run_maysync(m_inc(3)) == 4
        assert sync_await(m_inc(3)) == 5

        assert run_maysync(m_frob(3)) == 14
        assert sync_await(m_frob(3)) == 15

        assert run_maysync(m_grob(3)) == 134
        assert sync_await(m_grob(3)) == 135


##


async def m_tls_frob(i: int) -> int:
    return await m_inc(i + 10)


async def m_tls_grob(i: int) -> int:
    return await m_frob(i + 20) + 100


class TestTlsMaysync(unittest.TestCase):
    def test_tls_maysync(self):
        assert run_maysync(m_inc(3)) == 4
        assert sync_await(m_inc(3)) == 5

        assert run_maysync(m_tls_frob(3)) == 14
        assert sync_await(m_tls_frob(3)) == 15

        assert run_maysync(m_tls_grob(3)) == 134
        assert sync_await(m_tls_grob(3)) == 135


##


def s_gen(i: int) -> ta.Generator[int, None, None]:
    yield i + 1
    yield i + 2


async def a_gen(i: int) -> ta.AsyncGenerator[int, None]:
    yield i + 2
    yield i + 3


m_gen = make_maysync(s_gen, a_gen)


async def m_use_gen(i: int) -> int:
    c = 0
    async for j in m_gen(i):
        c += j
    return c


async def m_gen_frob(i: int) -> ta.AsyncGenerator[int, None]:
    await m_grob(i)
    async for j in m_gen(i):
        await m_grob(i)
        yield j + 10
    await m_grob(i)


async def m_gen_grob(i: int) -> ta.AsyncGenerator[int, None]:
    await m_grob(i)
    async for j in m_gen_frob(i + 20):
        await m_grob(i)
        yield j + 100
    await m_grob(i)


async def m_gen_grob_nested(i: int) -> ta.AsyncGenerator[int, None]:
    await m_grob(i)
    async for j in m_gen_frob(i + 20):
        async for k in m_gen_frob(j + 30):
            await m_grob(i)
            yield k + 1000
        yield j + 100
    await m_grob(i)


class TestMaysyncGenerators(unittest.TestCase):
    def test_maysync_generator(self):
        assert run_maysync(m_use_gen(3)) == 9
        assert sync_await(m_use_gen(3)) == 11

        assert list(run_maysync(m_gen(3))) == [4, 5]
        assert sync_async_list(m_gen(3)) == [5, 6]

        assert list(run_maysync(m_gen_frob(3))) == [14, 15]
        assert list(run_maysync(m_gen_grob(3))) == [134, 135]

        assert list(run_maysync(m_gen_grob_nested(3))) == [1075, 1076, 134, 1076, 1077, 135]
        assert sync_async_list(m_gen_grob_nested(3)) == [1077, 1078, 135, 1078, 1079, 136]


async def m_nest0(i: int) -> int:
    return (await m_inc(i)) + (await m_inc(i))


async def m_nest1(i: int) -> int:
    return (await m_nest0(i)) + (await m_nest0(i))


async def m_nest2(i: int) -> int:
    return (await m_nest1(i)) + (await m_nest1(i))


async def m_nest3(i: int) -> int:
    return (await m_nest2(i)) + (await m_nest2(i))


class TestNesting(unittest.TestCase):
    def test_nesting(self):
        assert run_maysync(m_nest3(3)) == 64
