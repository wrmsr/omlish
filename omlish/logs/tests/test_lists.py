# @omlish-lite
import logging
import unittest

from ..infos import LoggingContextInfos
from ..lists import ListAsyncLogger
from ..lists import ListLogger


class TestLogsLists(unittest.IsolatedAsyncioTestCase):
    def test_logs_lists(self):
        log = ListLogger(level=logging.INFO)
        log.info('hi')
        [e] = log.entries
        assert e.must_get_info(LoggingContextInfos.Caller).func_name == 'test_logs_lists'

    async def test_async_logs_lists(self):
        alog = ListAsyncLogger(level=logging.INFO)
        await alog.info('hi')
        [e] = alog.entries
        assert e.must_get_info(LoggingContextInfos.Caller).func_name == 'test_async_logs_lists'
