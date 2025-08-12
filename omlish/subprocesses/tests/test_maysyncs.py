# ruff: noqa: PT009 PT027
# @omlish-lite
import sys
import typing as ta
import unittest

from ...lite.check import check
from ..asyncs import AbstractAsyncSubprocesses
from ..maysyncs import MaysyncSubprocesses
from ..run import SubprocessRun
from ..run import SubprocessRunOutput
from ..sync import subprocesses


class BadError(Exception):
    pass


class BadAsyncSubprocesses(AbstractAsyncSubprocesses):
    def run_(self, run: SubprocessRun) -> ta.Awaitable[SubprocessRunOutput]:
        raise BadError

    def check_call(self, *cmd: str, stdout: ta.Any = sys.stderr, **kwargs: ta.Any) -> ta.Awaitable[None]:
        raise BadError

    def check_output(self, *cmd: str, **kwargs: ta.Any) -> ta.Awaitable[bytes]:
        raise BadError


maysync_subprocesses = MaysyncSubprocesses(
    subprocesses,
    BadAsyncSubprocesses(),
)


class TestMaysyncSubprocesses(unittest.TestCase):
    def test_subprocesses_output(self):
        maysync_subprocesses.check_output('echo', 'hi').s()
        self.assertEqual(check.not_none(maysync_subprocesses.try_output('echo', 'hi').s()).decode(), 'hi\n')
        self.assertIsNone(maysync_subprocesses.try_output('xcho', 'hi').s())
