import functools

import anyio
import pytest

from ..utils import gather


@pytest.mark.asyncs
# @pytest.mark.asyncio
async def test_gather():
    await gather(
        functools.partial(anyio.sleep, .02),
        functools.partial(anyio.sleep, .01),
        take_first=True,
    )
