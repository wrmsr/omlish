# @omlish-lite
from .....testing.unittest.asyncs import AsyncioIsolatedAsyncTestCase
from ..sleeps import AsyncioAsyncliteSleeps


class TestAsyncio(AsyncioIsolatedAsyncTestCase):
    async def test_sleep(self):
        await AsyncioAsyncliteSleeps().sleep(.2)
