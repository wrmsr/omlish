import unittest

from .. import providers as bp
from ..types import InterpSpecifier


class TestBaseProviders(unittest.IsolatedAsyncioTestCase):
    async def test_running(self):
        v = await bp.RunningInterpProvider().get_installed_versions(InterpSpecifier.parse('3.12'))
        print(await bp.RunningInterpProvider().get_installed_version(v[0]))
