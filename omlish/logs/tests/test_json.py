# @omlish-lite
import logging
import unittest

from ..json import JsonLogFormatter


class TestLogs(unittest.TestCase):
    def test_logs(self):
        for f in [
            JsonLogFormatter(),
        ]:
            handler = logging.StreamHandler()
            handler.setFormatter(f)

            log = logging.getLogger('_test')
            log.handlers.clear()
            log.handlers.append(handler)
            log.setLevel(logging.INFO)

            print()
            log.info('hi')
            log.warning('hi')
            log.error('hi')
