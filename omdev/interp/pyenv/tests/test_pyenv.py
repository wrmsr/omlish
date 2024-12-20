import sys
import unittest

from ...inspect import InterpInspector
from .. import pyenv as pe
from ..install import DarwinPyenvInstallOpts
from ..install import LinuxPyenvInstallOpts
from ..provider import PyenvInterpProvider


class TestPyenv(unittest.IsolatedAsyncioTestCase):
    @unittest.skipUnless(sys.platform == 'darwin', 'requires darwin')
    async def test_darwin(self):
        print(await DarwinPyenvInstallOpts().opts())

    @unittest.skipUnless(sys.platform == 'linux', 'requires linux')
    async def test_linux(self):
        print(await LinuxPyenvInstallOpts().opts())

    async def test_pyenv(self):
        p = PyenvInterpProvider(
            pyenv=pe.Pyenv(),
            inspector=InterpInspector(),
        )
        print(await p.installed())
