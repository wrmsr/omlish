# @omlish-lite
import logging
import unittest

from ..json import JsonLogFormatter


class TestJsonLogs(unittest.TestCase):
    def test_json_logs(self):
        for f in [
            JsonLogFormatter(),
        ]:
            handler = logging.StreamHandler()
            handler.setFormatter(f)

            log = logging.getLogger(__name__)
            log.handlers.clear()
            log.handlers.append(handler)
            log.setLevel(logging.INFO)

            print()
            log.info('hi')
            log.warning('hi')
            log.error('hi')
