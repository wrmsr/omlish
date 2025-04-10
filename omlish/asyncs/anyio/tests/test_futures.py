import anyio
import pytest

from .... import lang
from ..futures import create_future


@pytest.mark.asyncs
async def test_futs():
    async with anyio.create_task_group() as tg:
        fut = create_future[int]()

        o: lang.Outcome[int] | None = None

        async def a():
            nonlocal o
            with anyio.fail_after(1):
                o = await fut

        async def b():
            await anyio.sleep(.1)
            fut.set_value(420)

        tg.start_soon(a)
        tg.start_soon(b)

    assert o is not None
    assert o.value() == 420

    assert fut.outcome.present
    assert fut.outcome.must().value() == 420
