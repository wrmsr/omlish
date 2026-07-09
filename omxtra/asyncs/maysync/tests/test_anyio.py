import anyio
import pytest

from ..maysync import make_maysync
from ..maysync import run_maysync


def s_inc(i: int) -> int:
    return i + 1


async def a_inc(i: int) -> int:
    await anyio.sleep(.01)
    return i + 2


async def m_frob(i: int) -> int:
    return await make_maysync(s_inc, a_inc)(i)


async def m_grob(i: int) -> int:
    return await m_frob(i + 10) + 100


def test_maysync():
    assert run_maysync(m_frob(3)) == 4
    assert run_maysync(m_grob(3)) == 114


@pytest.mark.asyncs
async def test_anyio_maysync_all_backends():
    assert await m_frob(3) == 5
    assert await m_grob(3) == 115
