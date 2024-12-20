import sys
import unittest

from ...inspect import InterpInspector
from .. import pyenv as pe


class TestPyenv(unittest.IsolatedAsyncioTestCase):
    @unittest.skipUnless(sys.platform == 'darwin', 'requires darwin')
    async def test_darwin(self):
        print(await pe.DarwinPyenvInstallOpts().opts())

    @unittest.skipUnless(sys.platform == 'linux', 'requires linux')
    async def test_linux(self):
        print(await pe.LinuxPyenvInstallOpts().opts())

    async def test_pyenv(self):
        p = pe.PyenvInterpProvider(
            pyenv=pe.Pyenv(),
            inspector=InterpInspector(),
        )
        print(await p.installed())
