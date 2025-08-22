import unittest

from ..maysyncs import make_maysync
from ..maysyncs import maysync


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
        assert m_frob(3).s() == 14
        assert m_grob(3).s() == 134


# ##
#
#
# def s_gen(i: int) -> ta.Generator[int, None, None]:
#     yield i + 1
#     yield i + 2
#
#
# async def a_gen(i: int) -> ta.AsyncGenerator[int, None]:
#     yield i + 1
#     yield i + 2
#
#
# m_gen = make_maysync(s_gen, a_gen)
#
#
# @maysync
# async def m_gen_frob(i: int) -> int:
#     return await make_maysync(s_inc, a_inc)(i).m()
#
#
# @maysync
# async def m_gen_grob(i: int) -> int:
#     return await m_frob(i + 10).m() + 100
#
#
# class TestMaysyncGenerators(unittest.TestCase):
#     def test_maysync_generator(self):
#         assert m_inc(3).s() == 4
#         assert m_frob(3).s() == 4
#         assert m_grob(3).s() == 114
