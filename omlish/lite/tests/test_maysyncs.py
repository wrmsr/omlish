# ruff: noqa: UP043
import typing as ta
import unittest

from ..maysyncs import make_maysync
from ..maysyncs import maysync
from .utils import sync_async_list
from .utils import sync_await


##


def s_inc(i: int) -> int:
    return i + 1


async def a_inc(i: int) -> int:
    return i + 2


m_inc = make_maysync(s_inc, a_inc)


@maysync
async def m_frob(i: int) -> int:
    return await m_inc(i + 10).m()


@maysync
async def m_grob(i: int) -> int:
    return await m_frob(i + 20).m() + 100


class TestMaysync(unittest.TestCase):
    def test_maysync(self):
        assert m_inc(3).s() == 4
        assert sync_await(m_inc(3).a) == 5

        assert m_frob(3).s() == 14
        assert sync_await(m_frob(3).a) == 15

        assert m_grob(3).s() == 134
        assert sync_await(m_grob(3).a) == 135


##


def s_gen(i: int) -> ta.Generator[int, None, None]:
    yield i + 1
    yield i + 2


async def a_gen(i: int) -> ta.AsyncGenerator[int, None]:
    yield i + 2
    yield i + 3


m_gen = make_maysync(s_gen, a_gen)


@maysync
async def m_gen_frob(i: int) -> ta.AsyncGenerator[int, None]:
    await m_grob(i).m()
    async for j in m_gen(i).m():
        await m_grob(i).m()
        yield j + 10
    await m_grob(i).m()


@maysync
async def m_gen_grob(i: int) -> ta.AsyncGenerator[int, None]:
    await m_grob(i).m()
    async for j in m_gen_frob(i + 20).m():
        await m_grob(i).m()
        yield j + 100
    await m_grob(i).m()


class TestMaysyncGenerators(unittest.TestCase):
    def test_maysync_generator(self):
        assert list(m_gen(3).s()) == [4, 5]
        assert sync_async_list(m_gen(3).a) == [5, 6]

        assert list(m_gen_frob(3).s()) == [4, 5]
        # assert list(m_gen_grob(3).s()) == 114
