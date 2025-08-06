from ..maysync_ import MaysyncGen
from ..maysync_ import maysync
from ..maysync_ import maysync_yield


def _inc(i: int) -> int:
    return i + 1


async def _a_inc(i: int) -> int:
    return i + 1


def _m_frob(i: int) -> MaysyncGen[int]:
    return (yield from maysync_yield(_inc, _a_inc)(i))


def test_maysync():
    assert maysync(_m_frob, 3) == 4
