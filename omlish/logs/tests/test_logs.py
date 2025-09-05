# @omlish-lite
import logging
import os.path
import unittest

from ..std.adapters import StdLogger
from ..std.handlers import ListLoggingHandler
from ..std.records import LoggingContextLogRecord


class TestLogs(unittest.TestCase):
    def test_logs(self):
        handler = ListLoggingHandler()

        log = logging.getLogger(__name__)
        log.handlers.clear()
        log.handlers.append(handler)
        log.setLevel(logging.INFO)

        log.info('hi')
        log.warning('hi')
        log.error('hi')

        std_log = StdLogger(log)

        std_log.info('hi')
        std_log.warning('hi')
        std_log.error('hi')

        std_log.info(lambda: 'hi')
        std_log.info(lambda: ('hi %d', 420))

        std_log.info(('hi',))
        std_log.info(('hi %d', 420))

        lr = handler.records[-1]
        assert isinstance(lr, LoggingContextLogRecord)
        assert os.path.basename(lr.pathname) == 'test_logs.py'
        assert lr.funcName == 'test_logs'
