# ruff: noqa: PT009 UP006 UP007
import shutil
import unittest

from .harness import CiHarness


class TestCi(unittest.IsolatedAsyncioTestCase):
    async def test_ci(self):
        if not shutil.which('docker'):
            self.skipTest('no docker')

        async with CiHarness() as ci_harness:
            async with ci_harness.make_ci() as ci:
                await ci.run()
