import unittest

from ..sleeps import AsyncioAsyncliteSleeps


class TestAsyncio(unittest.IsolatedAsyncioTestCase):
    async def test_sleep(self):
        await AsyncioAsyncliteSleeps().sleep(.2)
