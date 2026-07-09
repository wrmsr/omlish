import sys
import typing as ta

import pytest

from omlish import check
from omlish.asyncs.asyncio.subprocesses import asyncio_subprocesses
from omlish.subprocesses.run import SubprocessRun
from omlish.subprocesses.run import SubprocessRunOutput
from omlish.subprocesses.sync import AbstractSubprocesses

from ..subprocesses import MaysyncSubprocesses


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
