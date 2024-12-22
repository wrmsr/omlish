import unittest

from ..uv import Uv
from ..uv import UvConfig


class TestUv(unittest.IsolatedAsyncioTestCase):
    async def test_uv(self):
        uv = Uv(UvConfig(
            ignore_path=True,
            pip_bootstrap=True,
        ))
        print(await uv.uv_exe())
