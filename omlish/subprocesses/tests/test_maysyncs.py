# ruff: noqa: PT009 PT027
# @omlish-lite
import typing as ta
import unittest

from ...lite.check import check
from ...lite.maysyncs import run_maysync
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


maysync_subprocesses = MaysyncSubprocesses(
    subprocesses,
    BadAsyncSubprocesses(),
)


class TestMaysyncSubprocesses(unittest.TestCase):
    def test_subprocesses_output(self):
        run_maysync(maysync_subprocesses.check_output('echo', 'hi'))
        self.assertEqual(check.not_none(run_maysync(maysync_subprocesses.try_output('echo', 'hi'))).decode(), 'hi\n')  # noqa
        self.assertIsNone(run_maysync(maysync_subprocesses.try_output('xcho', 'hi')))
