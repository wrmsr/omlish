import unittest

from ..asyncio.sleeps import AsyncioAsyncliteSleeps


class TestAsyncio(unittest.IsolatedAsyncioTestCase):
    async def test_sleep(self):
        await AsyncioAsyncliteSleeps().sleep(.2)
