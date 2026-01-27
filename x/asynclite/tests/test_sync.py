import unittest

from ..sync.sleeps import SyncAsyncliteSleeps


class TestSync(unittest.TestCase):
    def test_sleep(self):
        SyncAsyncliteSleeps().sleep(.2)
