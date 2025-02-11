# ruff: noqa: UP006 UP007
# @omlish-lite
import abc
import sys
import typing as ta

from ..lite.timeouts import TimeoutLike
from .base import BaseSubprocesses
from .run import SubprocessRun
from .run import SubprocessRunOutput


##


class AbstractAsyncSubprocesses(BaseSubprocesses):
    @abc.abstractmethod
    async def run_(self, run: SubprocessRun) -> SubprocessRunOutput:
        raise NotImplementedError

    def run(
            self,
            *cmd: str,
            input: ta.Any = None,  # noqa
            timeout: ta.Optional[TimeoutLike] = None,
            check: bool = False,
            capture_output: ta.Optional[bool] = None,
            **kwargs: ta.Any,
    ) -> ta.Awaitable[SubprocessRunOutput]:
        return self.run_(SubprocessRun(
            cmd=cmd,
            input=input,
            timeout=timeout,
            check=check,
            capture_output=capture_output,
            kwargs=kwargs,
        ))

    #

    @abc.abstractmethod
    async def check_call(
            self,
            *cmd: str,
            stdout: ta.Any = sys.stderr,
            **kwargs: ta.Any,
    ) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def check_output(
            self,
            *cmd: str,
            **kwargs: ta.Any,
    ) -> bytes:
        raise NotImplementedError

    #

    async def check_output_str(
            self,
            *cmd: str,
            **kwargs: ta.Any,
    ) -> str:
        return (await self.check_output(*cmd, **kwargs)).decode().strip()

    #

    async def try_call(
            self,
            *cmd: str,
            **kwargs: ta.Any,
    ) -> bool:
        if isinstance(await self.async_try_fn(self.check_call, *cmd, **kwargs), Exception):
            return False
        else:
            return True

    async def try_output(
            self,
            *cmd: str,
            **kwargs: ta.Any,
    ) -> ta.Optional[bytes]:
        if isinstance(ret := await self.async_try_fn(self.check_output, *cmd, **kwargs), Exception):
            return None
        else:
            return ret

    async def try_output_str(
            self,
            *cmd: str,
            **kwargs: ta.Any,
    ) -> ta.Optional[str]:
        if (ret := await self.try_output(*cmd, **kwargs)) is None:
            return None
        else:
            return ret.decode().strip()
