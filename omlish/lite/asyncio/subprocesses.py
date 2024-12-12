# ruff: noqa: UP006 UP007
import asyncio.base_subprocess
import asyncio.subprocess
import contextlib
import dataclasses as dc
import functools
import subprocess
import sys
import typing as ta

from ...asyncs.asyncio.timeouts import asyncio_maybe_timeout
from ..check import check
from ..logs import log
from ..subprocesses import AbstractSubprocesses


T = ta.TypeVar('T')


##


class AsyncioProcessCommunicator:
    def __init__(
            self,
            proc: asyncio.subprocess.Process,
            loop: ta.Optional[ta.Any] = None,
    ) -> None:
        super().__init__()

        if loop is None:
            loop = asyncio.get_running_loop()

        self._proc = proc
        self._loop = loop

        self._transport: asyncio.base_subprocess.BaseSubprocessTransport = check.isinstance(
            proc._transport,  # type: ignore  # noqa
            asyncio.base_subprocess.BaseSubprocessTransport,
        )

    @property
    def _debug(self) -> bool:
        return self._loop.get_debug()

    async def _feed_stdin(self, input: bytes) -> None:  # noqa
        stdin = check.not_none(self._proc.stdin)
        try:
            if input is not None:
                stdin.write(input)
                if self._debug:
                    log.debug('%r communicate: feed stdin (%s bytes)', self, len(input))

            await stdin.drain()

        except (BrokenPipeError, ConnectionResetError) as exc:
            # communicate() ignores BrokenPipeError and ConnectionResetError. write() and drain() can raise these
            # exceptions.
            if self._debug:
                log.debug('%r communicate: stdin got %r', self, exc)

        if self._debug:
            log.debug('%r communicate: close stdin', self)

        stdin.close()

    async def _noop(self) -> None:
        return None

    async def _read_stream(self, fd: int) -> bytes:
        transport: ta.Any = check.not_none(self._transport.get_pipe_transport(fd))

        if fd == 2:
            stream = check.not_none(self._proc.stderr)
        else:
            check.equal(fd, 1)
            stream = check.not_none(self._proc.stdout)

        if self._debug:
            name = 'stdout' if fd == 1 else 'stderr'
            log.debug('%r communicate: read %s', self, name)

        output = await stream.read()

        if self._debug:
            name = 'stdout' if fd == 1 else 'stderr'
            log.debug('%r communicate: close %s', self, name)

        transport.close()

        return output

    class Communication(ta.NamedTuple):
        stdout: ta.Optional[bytes]
        stderr: ta.Optional[bytes]

    async def _communicate(
            self,
            input: ta.Any = None,  # noqa
    ) -> Communication:
        stdin_fut: ta.Any
        if self._proc.stdin is not None:
            stdin_fut = self._feed_stdin(input)
        else:
            stdin_fut = self._noop()

        stdout_fut: ta.Any
        if self._proc.stdout is not None:
            stdout_fut = self._read_stream(1)
        else:
            stdout_fut = self._noop()

        stderr_fut: ta.Any
        if self._proc.stderr is not None:
            stderr_fut = self._read_stream(2)
        else:
            stderr_fut = self._noop()

        stdin_res, stdout_res, stderr_res = await asyncio.gather(stdin_fut, stdout_fut, stderr_fut)

        await self._proc.wait()

        return AsyncioProcessCommunicator.Communication(stdout_res, stderr_res)

    async def communicate(
            self,
            input: ta.Any = None,  # noqa
            timeout: ta.Optional[float] = None,
    ) -> Communication:
        return await asyncio_maybe_timeout(self._communicate(input), timeout)


##


class AsyncioSubprocesses(AbstractSubprocesses):
    async def communicate(
            self,
            proc: asyncio.subprocess.Process,
            input: ta.Any = None,  # noqa
            timeout: ta.Optional[float] = None,
    ) -> ta.Tuple[ta.Optional[bytes], ta.Optional[bytes]]:
        return await AsyncioProcessCommunicator(proc).communicate(input, timeout)  # noqa

    #

    @contextlib.asynccontextmanager
    async def popen(
            self,
            *cmd: str,
            shell: bool = False,
            timeout: ta.Optional[float] = None,
            **kwargs: ta.Any,
    ) -> ta.AsyncGenerator[asyncio.subprocess.Process, None]:
        fac: ta.Any
        if shell:
            fac = functools.partial(
                asyncio.create_subprocess_shell,
                check.single(cmd),
            )
        else:
            fac = functools.partial(
                asyncio.create_subprocess_exec,
                *cmd,
            )

        with self.prepare_and_wrap( *cmd, shell=shell, **kwargs) as (cmd, kwargs):  # noqa
            proc: asyncio.subprocess.Process = await fac(**kwargs)
            try:
                yield proc

            finally:
                await asyncio_maybe_timeout(proc.wait(), timeout)

    #

    @dc.dataclass(frozen=True)
    class RunOutput:
        proc: asyncio.subprocess.Process
        stdout: ta.Optional[bytes]
        stderr: ta.Optional[bytes]

    async def run(
            self,
            *cmd: str,
            input: ta.Any = None,  # noqa
            timeout: ta.Optional[float] = None,
            check: bool = False,  # noqa
            capture_output: ta.Optional[bool] = None,
            **kwargs: ta.Any,
    ) -> RunOutput:
        if capture_output:
            kwargs.setdefault('stdout', subprocess.PIPE)
            kwargs.setdefault('stderr', subprocess.PIPE)

        proc: asyncio.subprocess.Process
        async with self.popen(*cmd, **kwargs) as proc:
            stdout, stderr = await self.communicate(proc, input, timeout)

        if check and proc.returncode:
            raise subprocess.CalledProcessError(
                proc.returncode,
                cmd,
                output=stdout,
                stderr=stderr,
            )

        return self.RunOutput(
            proc,
            stdout,
            stderr,
        )

    #

    async def check_call(
            self,
            *cmd: str,
            stdout: ta.Any = sys.stderr,
            **kwargs: ta.Any,
    ) -> None:
        with self.prepare_and_wrap(*cmd, stdout=stdout, check=True, **kwargs) as (cmd, kwargs):  # noqa
            await self.run(*cmd, **kwargs)

    async def check_output(
            self,
            *cmd: str,
            **kwargs: ta.Any,
    ) -> bytes:
        with self.prepare_and_wrap(*cmd, stdout=subprocess.PIPE, check=True, **kwargs) as (cmd, kwargs):  # noqa
            return check.not_none((await self.run(*cmd, **kwargs)).stdout)

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


asyncio_subprocesses = AsyncioSubprocesses()
