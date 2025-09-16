import pytest

from ..asyncs import as_async


@pytest.mark.asyncs('asyncio')
async def test_as_async():
    assert (await as_async(lambda: 420)()) == 420
