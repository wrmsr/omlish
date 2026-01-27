import unittest

from ..sleeps import SyncAsyncliteSleeps


class TestSync(unittest.TestCase):
    def test_sleep(self):
        SyncAsyncliteSleeps().sleep(.2)
