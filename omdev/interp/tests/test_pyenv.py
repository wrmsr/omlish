import sys
import unittest

from .. import pyenv as pe


class TestPyenv(unittest.IsolatedAsyncioTestCase):
    @unittest.skipUnless(sys.platform == 'darwin', 'requires darwin')
    async def test_darwin(self):
        print(await pe.DarwinPyenvInstallOpts().opts())

    @unittest.skipUnless(sys.platform == 'linux', 'requires linux')
    async def test_linux(self):
        print(await pe.LinuxPyenvInstallOpts().opts())

    async def test_pyenv(self):
        p = pe.PyenvInterpProvider()
        print(await p.installed())
