# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import sys
import typing as ta

from ..lite.maysync import make_maysync
from .asyncs import AbstractAsyncSubprocesses
from .run import SubprocessRun
from .run import SubprocessRunOutput
from .sync import AbstractSubprocesses


##


class MaysyncSubprocesses(AbstractAsyncSubprocesses):
    def __init__(
            self,
            subprocesses: AbstractSubprocesses,
            async_subprocesses: AbstractAsyncSubprocesses,
    ) -> None:
        super().__init__()

        self._subprocesses = subprocesses
        self._async_subprocesses = async_subprocesses

    #

    def run_(self, run: SubprocessRun) -> ta.Awaitable[SubprocessRunOutput]:
        return make_maysync(
            self._subprocesses.run,
            self._async_subprocesses.run,
        )(run)

    #

    async def check_call(
            self,
            *cmd: str,
            stdout: ta.Any = sys.stderr,
            **kwargs: ta.Any,
    ) -> None:
        return await make_maysync(
            self._subprocesses.check_call,
            self._async_subprocesses.check_call,
        )(*cmd, stdout=stdout, **kwargs)

    async def check_output(
            self,
            *cmd: str,
            **kwargs: ta.Any,
    ) -> bytes:
        return await make_maysync(
            self._subprocesses.check_output,
            self._async_subprocesses.check_output,
        )(*cmd, **kwargs)
