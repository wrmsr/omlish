import sys
import typing as ta

import pytest

from .... import check
from ....subprocesses.maysync import MaysyncSubprocesses
from ....subprocesses.run import SubprocessRun
from ....subprocesses.run import SubprocessRunOutput
from ....subprocesses.sync import AbstractSubprocesses
from ..subprocesses import asyncio_subprocesses


##


@pytest.mark.asyncs('asyncio')
async def test_subprocesses():
    out = await asyncio_subprocesses.check_output('echo 42', shell=True)
    assert int(out.decode().strip()) == 42
    assert check.not_none(await asyncio_subprocesses.try_output('echo', 'hi')).decode() == 'hi\n'
    assert (await asyncio_subprocesses.try_output('xcho', 'hi')) is None


##


class BadError(Exception):
    pass


class BadSubprocesses(AbstractSubprocesses):
    def run_(self, run: SubprocessRun) -> SubprocessRunOutput:
        raise BadError

    def check_call(self, *cmd: str, stdout: ta.Any = sys.stderr, **kwargs: ta.Any) -> None:
        raise BadError

    def check_output(self, *cmd: str, **kwargs: ta.Any) -> bytes:
        raise BadError


maysync_subprocesses = MaysyncSubprocesses(
    BadSubprocesses(),
    asyncio_subprocesses,
)


@pytest.mark.asyncs('asyncio')
async def test_maysync_subprocesses():
    out = await maysync_subprocesses.check_output('echo 42', shell=True)
    assert int(out.decode().strip()) == 42
    assert check.not_none(await maysync_subprocesses.try_output('echo', 'hi')).decode() == 'hi\n'
    assert (await maysync_subprocesses.try_output('xcho', 'hi')) is None
