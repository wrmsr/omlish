# @omlish-lite
import logging
import unittest

from ..asyncs import AsyncLoggerToLogger
from ..asyncs import LoggerToAsyncLogger
from ..infos import LoggingContextInfos
from ..lists import ListAsyncLogger
from ..lists import ListLogger


class TestLogsAsyncs(unittest.IsolatedAsyncioTestCase):
    def test_a2s(self):
        u = ListAsyncLogger(level=logging.INFO)
        log = AsyncLoggerToLogger(u)
        log.info('hi')
        [e] = u.entries
        assert e.must_get_info(LoggingContextInfos.Caller).func_name == 'test_a2s'

    async def test_s2a(self):
        u = ListLogger(level=logging.INFO)
        alog = LoggerToAsyncLogger(u)
        await alog.info('hi')
        [e] = u.entries
        assert e.must_get_info(LoggingContextInfos.Caller).func_name == 'test_s2a'
