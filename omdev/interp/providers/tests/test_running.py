import unittest

from ...types import InterpSpecifier
from ..running import RunningInterpProvider


class TestBaseProviders(unittest.IsolatedAsyncioTestCase):
    async def test_running(self):
        v = await RunningInterpProvider().get_installed_versions(InterpSpecifier.parse('3.13'))
        print(await RunningInterpProvider().get_installed_version(v[0]))
