from ..maysyncs import make_maysync
from ..maysyncs import maysync


def s_inc(i: int) -> int:
    return i + 1


async def a_inc(i: int) -> int:
    return i + 1


@maysync
async def m_frob(i: int) -> int:
    return await make_maysync(s_inc, a_inc).m(i)


def test_maysync():
    assert m_frob.s(3) == 4
