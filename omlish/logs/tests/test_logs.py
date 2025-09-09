# @omlish-lite
import logging
import os.path
import unittest

from ..std.handlers import ListLoggingHandler
from ..std.loggers import StdLogger
from ..std.records import LoggingContextLogRecord


class TestLogs(unittest.TestCase):
    def test_logs(self):
        handler = ListLoggingHandler()

        logging_log = logging.getLogger(__name__)
        logging_log.handlers.clear()
        logging_log.handlers.append(handler)
        logging_log.setLevel(logging.INFO)

        logging_log.info('hi')
        logging_log.warning('hi')
        logging_log.error('hi')

        log = StdLogger(logging_log)

        log.info('hi')
        log.warning('hi')
        log.error('hi')

        log.info(lambda: 'hi')
        log.info(lambda: ('hi %d', 420))

        log.info(('hi',))
        log.info(('hi %d', 420))

        lr = handler.records[-1]
        assert isinstance(lr, LoggingContextLogRecord)
        assert os.path.basename(lr.pathname) == 'test_logs.py'
        assert lr.funcName == 'test_logs'

        i = 420
        log.info(f'hi! {i}')  # noqa

        c = 0

        def foo() -> str:
            nonlocal c
            c += 1
            return f'foo:{c}'

        log.info(f'{foo()}')  # noqa
        assert c == 1

        log.info(lambda: f'{foo()}')
        assert c == 2

        log.debug(f'{foo()}')  # noqa
        assert c == 3

        log.debug(lambda: f'{foo()}')
        assert c == 3
