import unittest

from .. import system as sp
from ..types import InterpSpecifier


class TestBaseProviders(unittest.IsolatedAsyncioTestCase):
    async def test_system(self):
        v = await sp.SystemInterpProvider().get_installed_versions(InterpSpecifier.parse('3.12'))
        print(await sp.SystemInterpProvider().get_installed_version(v[0]))

    def test_system_exes(self):
        print(sp.SystemInterpProvider().exes())
