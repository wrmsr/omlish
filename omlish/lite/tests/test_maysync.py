import unittest

from ..maysync import MaysyncGen
from ..maysync import maysync
from ..maysync import maysync_op


def _inc(i: int) -> int:
    return i + 1


async def _a_inc(i: int) -> int:
    return i + 1


def _m_frob(i: int) -> MaysyncGen[int]:
    return (yield maysync_op(_inc, _a_inc)(i))


class TestMaysync(unittest.TestCase):
    def test_maysync(self):
        assert maysync(_m_frob, 3) == 4
