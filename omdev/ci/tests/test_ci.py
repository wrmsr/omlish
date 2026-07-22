# ruff: noqa: PT009 UP006 UP007
import shutil
import unittest

from omcore.lite.tests.pytest import pytest_mark
from omcore.testing.unittest.skips import unittest_mark

from .harness import CiHarness


class TestCi(unittest.IsolatedAsyncioTestCase):
    @pytest_mark('timeout', 5 * 60)
    @pytest_mark('slow')
    @pytest_mark('online')
    @unittest_mark('slow')
    @unittest_mark('online')
    async def test_ci(self):
        if not shutil.which('docker'):
            self.skipTest('no docker')

        async with CiHarness() as ci_harness:
            async with ci_harness.make_ci() as ci:
                await ci.run()
