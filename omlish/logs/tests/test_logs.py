# @omlish-lite
import logging
import unittest

from ..handlers import ListHandler
from ..protocol import StdlibLogging


class TestLogs(unittest.TestCase):
    def test_logs(self):
        handler = ListHandler()

        log = logging.getLogger(__name__)
        log.handlers.clear()
        log.handlers.append(handler)
        log.setLevel(logging.INFO)

        log.info('hi')
        log.warning('hi')
        log.error('hi')

        std_log = StdlibLogging(log)

        std_log.info('hi')
        std_log.warning('hi')
        std_log.error('hi')
