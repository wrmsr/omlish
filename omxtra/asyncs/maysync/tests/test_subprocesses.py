# ruff: noqa: PT009 PT027
# @om-lite
import typing as ta
import unittest

from omcore.lite.check import check
from omcore.subprocesses.asyncs import AbstractAsyncSubprocesses
from omcore.subprocesses.run import SubprocessRun
from omcore.subprocesses.run import SubprocessRunOutput
from omcore.subprocesses.sync import subprocesses

from ..lite.maysync import run_maysync
from ..subprocesses import MaysyncSubprocesses


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
