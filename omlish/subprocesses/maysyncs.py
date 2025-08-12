# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import abc
import sys
import typing as ta

from ..lite.maysyncs import Maywaitable
from ..lite.maysyncs import make_maysync
from ..lite.maysyncs import maysync
from ..lite.timeouts import TimeoutLike
from .asyncs import AbstractAsyncSubprocesses
from .base import BaseSubprocesses
from .run import SubprocessRun
from .run import SubprocessRunOutput
from .sync import AbstractSubprocesses


##


class AbstractMaysyncSubprocesses(BaseSubprocesses, abc.ABC):
    @abc.abstractmethod
    def run_(self, run: SubprocessRun) -> Maywaitable[SubprocessRunOutput]:
        raise NotImplementedError

    def run(
            self,
            *cmd: str,
            input: ta.Any = None,  # noqa
            timeout: TimeoutLike = None,
            check: bool = False,
            capture_output: ta.Optional[bool] = None,
            **kwargs: ta.Any,
    ) -> Maywaitable[SubprocessRunOutput]:
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
    def check_call(
            self,
            *cmd: str,
            stdout: ta.Any = sys.stderr,
            **kwargs: ta.Any,
    ) -> Maywaitable[None]:
        raise NotImplementedError

    @abc.abstractmethod
    def check_output(
            self,
            *cmd: str,
            **kwargs: ta.Any,
    ) -> Maywaitable[bytes]:
        raise NotImplementedError

    #

    @maysync
    async def check_output_str(
            self,
            *cmd: str,
            **kwargs: ta.Any,
    ) -> str:
        return (await self.check_output(*cmd, **kwargs).m()).decode().strip()

    #

    @maysync
    async def try_call(
            self,
            *cmd: str,
            **kwargs: ta.Any,
    ) -> bool:
        if isinstance(await self.async_try_fn(self.check_call(*cmd, **kwargs).m), Exception):
            return False
        else:
            return True

    @maysync
    async def try_output(
            self,
            *cmd: str,
            **kwargs: ta.Any,
    ) -> ta.Optional[bytes]:
        if isinstance(ret := await self.async_try_fn(self.check_output(*cmd, **kwargs).m), Exception):
            return None
        else:
            return ret

    @maysync
    async def try_output_str(
            self,
            *cmd: str,
            **kwargs: ta.Any,
    ) -> ta.Optional[str]:
        if (ret := await self.try_output(*cmd, **kwargs).m()) is None:
            return None
        else:
            return ret.decode().strip()


##


class MaysyncSubprocesses(AbstractMaysyncSubprocesses):
    def __init__(
            self,
            subprocesses: AbstractSubprocesses,
            async_subprocesses: AbstractAsyncSubprocesses,
    ) -> None:
        super().__init__()

        self._subprocesses = subprocesses
        self._async_subprocesses = async_subprocesses

    #

    def run_(self, run: SubprocessRun) -> Maywaitable[SubprocessRunOutput]:
        return make_maysync(
            self._subprocesses.run,
            self._async_subprocesses.run,
        )(run)

    #

    def check_call(
            self,
            *cmd: str,
            stdout: ta.Any = sys.stderr,
            **kwargs: ta.Any,
    ) -> Maywaitable[None]:
        return make_maysync(
            self._subprocesses.check_call,
            self._async_subprocesses.check_call,
        )(*cmd, stdout=stdout, **kwargs)

    def check_output(
            self,
            *cmd: str,
            **kwargs: ta.Any,
    ) -> Maywaitable[bytes]:
        return make_maysync(
            self._subprocesses.check_output,
            self._async_subprocesses.check_output,
        )(*cmd, **kwargs)
