# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import abc
import sys
import typing as ta

from ..lite.timeouts import TimeoutLike
from .base import BaseSubprocesses
from .run import SubprocessRun
from .run import SubprocessRunOutput
from .async_ import _AbstractAsyncSubprocesses



##


class AbstractMaysyncSubprocesses(_AbstractAsyncSubprocesses, abc.ABC):
    pass


##


class MaysyncSubprocesses(AbstractMaysyncSubprocesses):
    async def run_(self, run: SubprocessRun) -> SubprocessRunOutput:
        raise NotImplementedError

    async def check_call(self, *cmd: str, stdout: ta.Any = sys.stderr, **kwargs: ta.Any) -> None:
        raise NotImplementedError

    async def check_output(self, *cmd: str, **kwargs: ta.Any) -> bytes:
        raise NotImplementedError
