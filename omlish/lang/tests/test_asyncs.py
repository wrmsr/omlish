import asyncio
import typing as ta

import pytest

from ..asyncs import as_async
from ..asyncs import async_generator_with_return


@pytest.mark.asyncs('asyncio')
async def test_as_async():
    assert (await as_async(lambda: 420)()) == 420


@pytest.mark.asyncs('asyncio')
async def test_async_generator_with_return():
    async def ag(n: int) -> ta.AsyncGenerator[int]:
        for i in range(n):
            await asyncio.sleep(.1)
            yield i + 10

    async for j in ag(3):
        print(j)

    @async_generator_with_return
    async def agv(set_value: ta.Callable[[int], None], n: int) -> ta.AsyncGenerator[int]:
        for i in range(n):
            await asyncio.sleep(.1)
            yield i + 10
        set_value(n + 20)

    # if ta.TYPE_CHECKING:
    #     ta.reveal_type(agv)

    async for j in (gr := agv(3)):
        print(j)
    print(gr.value.must())
