# @omlish-lite
import unittest

from ..sleeps import SyncAsyncliteSleeps


class TestSync(unittest.TestCase):
    async def test_sleep(self):
        await SyncAsyncliteSleeps().sleep(.2)
