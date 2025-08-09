import unittest

from ..maysyncs import make_maysyncable
from ..maysyncs import maysyncable


def s_inc(i: int) -> int:
    return i + 1


async def a_inc(i: int) -> int:
    return i + 1


@maysyncable
async def m_frob(i: int) -> int:
    return await make_maysyncable(s_inc, a_inc).m(i)


class TestMaysync(unittest.TestCase):
    def test_maysync(self):
        assert m_frob.s(3) == 4
