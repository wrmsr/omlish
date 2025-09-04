import logging
import unittest

from ..levels import NamedLogLevel


class TestNamedLogLevel(unittest.TestCase):
    def test_named_log_level(self):
        d1 = logging.DEBUG + 1
        assert str(NamedLogLevel(d1)) == f'DEBUG:{d1}'
        assert repr(NamedLogLevel(d1)) == f'NamedLogLevel({d1})'

        assert NamedLogLevel.INFO.exact_name == 'INFO'
        assert NamedLogLevel.INFO.effective_name == 'INFO'
        assert NamedLogLevel.INFO._effective_name == 'INFO'  # noqa

        i2 = NamedLogLevel(logging.INFO + 2)
        assert i2.exact_name is None
        assert i2.effective_name == 'INFO'
        assert NamedLogLevel.INFO._effective_name == 'INFO'  # noqa

        assert NamedLogLevel(logging.INFO) == logging.INFO
        assert logging.INFO == NamedLogLevel(logging.INFO)

        assert NamedLogLevel(logging.INFO) < logging.WARNING
        assert logging.INFO < NamedLogLevel(logging.WARNING)
        assert NamedLogLevel(logging.WARNING) > logging.INFO
        assert logging.WARNING > NamedLogLevel(logging.INFO)

        assert str(NamedLogLevel(logging.INFO)) == 'INFO'
        assert repr(NamedLogLevel(logging.INFO)) == f'NamedLogLevel({logging.INFO})'
