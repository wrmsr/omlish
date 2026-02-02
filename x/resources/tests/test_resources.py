import pytest

from ..resources import AsyncResources


@pytest.mark.asyncs('asyncio')
async def test_async_resources():
    async with AsyncResources.new() as resources:
        pass
