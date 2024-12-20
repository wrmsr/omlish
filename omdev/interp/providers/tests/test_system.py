import unittest

from ...inspect import InterpInspector
from ...types import InterpSpecifier
from ..system import SystemInterpProvider


class TestBaseProviders(unittest.IsolatedAsyncioTestCase):
    async def test_system(self):
        v = await SystemInterpProvider(
            inspector=InterpInspector(),
        ).get_installed_versions(InterpSpecifier.parse('3.12'))

        print(await SystemInterpProvider(
            inspector=InterpInspector(),
        ).get_installed_version(v[0]))

    def test_system_exes(self):
        print(SystemInterpProvider().exes())
