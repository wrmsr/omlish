import unittest

from ..pycharm import PycharmRemoteDebug
from ..pycharm import pycharm_debug_preamble


class TestPycharm(unittest.TestCase):
    def test_debug_preamble_compiles(self):
        for prd in [
            PycharmRemoteDebug(5678),
            PycharmRemoteDebug(5678, host='farhost', install_version=None),
        ]:
            src = pycharm_debug_preamble(prd)
            compile(src, '<preamble>', 'exec')
