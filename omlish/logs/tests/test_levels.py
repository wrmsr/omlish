# @omlish-lite
import logging
import unittest

from ..levels import NamedLogLevel


class TestNamedLogLevel(unittest.TestCase):
    def test_named_log_level(self):
        for _ in range(2):
            assert str(NamedLogLevel(logging.DEBUG)) == f'DEBUG'
            assert repr(NamedLogLevel(logging.DEBUG)) == f"NamedLogLevel('DEBUG')"

        d1 = logging.DEBUG + 1
        assert str(NamedLogLevel(d1)) == f'DEBUG+{d1}'
        assert repr(NamedLogLevel(d1)) == f"NamedLogLevel('DEBUG', 1)"

        assert NamedLogLevel.INFO.exact_name == 'INFO'
        assert NamedLogLevel.INFO.effective_name == 'INFO'

        i2 = NamedLogLevel(logging.INFO + 2)
        assert i2.exact_name is None
        assert i2.effective_name == 'INFO'
        assert NamedLogLevel.INFO.effective_name == 'INFO'  # noqa

        assert NamedLogLevel(logging.INFO) == logging.INFO
        assert logging.INFO == NamedLogLevel(logging.INFO)

        assert NamedLogLevel(logging.INFO) < logging.WARNING
        assert logging.INFO < NamedLogLevel(logging.WARNING)
        assert NamedLogLevel(logging.WARNING) > logging.INFO
        assert logging.WARNING > NamedLogLevel(logging.INFO)

        assert str(NamedLogLevel(logging.INFO)) == 'INFO'
        assert repr(NamedLogLevel(logging.INFO)) == f"NamedLogLevel('INFO')"

        assert NamedLogLevel('info') == logging.INFO
