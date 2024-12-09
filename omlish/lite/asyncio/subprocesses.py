# ruff: noqa: UP006 UP007
import asyncio.base_subprocess
import asyncio.subprocess
import contextlib
import functools
import logging
import subprocess
import sys
import typing as ta

from ..check import check_equal
from ..check import check_isinstance
from ..check import check_not_none
from ..check import check_single
from ..logs import log
from ..subprocesses import DEFAULT_SUBPROCESS_TRY_EXCEPTIONS
from ..subprocesses import prepare_subprocess_invocation
from ..subprocesses import subprocess_common_context
from .asyncio import asyncio_maybe_timeout


T = ta.TypeVar('T')


##


@contextlib.asynccontextmanager
async def asyncio_subprocess_popen(
        *cmd: str,
        shell: bool = False,
        timeout: ta.Optional[float] = None,
        **kwargs: ta.Any,
) -> ta.AsyncGenerator[asyncio.subprocess.Process, None]:
    fac: ta.Any
    if shell:
        fac = functools.partial(
            asyncio.create_subprocess_shell,
            check_single(cmd),
        )
    else:
        fac = functools.partial(
            asyncio.create_subprocess_exec,
            *cmd,
        )

    with subprocess_common_context(
            *cmd,
            shell=shell,
            timeout=timeout,
            **kwargs,
    ):
        proc: asyncio.subprocess.Process
        proc = await fac(**kwargs)
        try:
            yield proc

        finally:
            await asyncio_maybe_timeout(proc.wait(), timeout)


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

        self._transport: asyncio.base_subprocess.BaseSubprocessTransport = check_isinstance(
            proc._transport,  # type: ignore  # noqa
            asyncio.base_subprocess.BaseSubprocessTransport,
        )

    @property
    def _debug(self) -> bool:
        return self._loop.get_debug()

    async def _feed_stdin(self, input: bytes) -> None:  # noqa
        stdin = check_not_none(self._proc.stdin)
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
        transport: ta.Any = check_not_none(self._transport.get_pipe_transport(fd))

        if fd == 2:
            stream = check_not_none(self._proc.stderr)
        else:
            check_equal(fd, 1)
            stream = check_not_none(self._proc.stdout)

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


async def asyncio_subprocess_communicate(
        proc: asyncio.subprocess.Process,
        input: ta.Any = None,  # noqa
        timeout: ta.Optional[float] = None,
) -> ta.Tuple[ta.Optional[bytes], ta.Optional[bytes]]:
    return await AsyncioProcessCommunicator(proc).communicate(input, timeout)  # noqa


##


async def _asyncio_subprocess_check_run(
        *args: str,
        input: ta.Any = None,  # noqa
        timeout: ta.Optional[float] = None,
        **kwargs: ta.Any,
) -> ta.Tuple[ta.Optional[bytes], ta.Optional[bytes]]:
    args, kwargs = prepare_subprocess_invocation(*args, **kwargs)

    proc: asyncio.subprocess.Process
    async with asyncio_subprocess_popen(*args, **kwargs) as proc:
        stdout, stderr = await asyncio_subprocess_communicate(proc, input, timeout)

    if proc.returncode:
        raise subprocess.CalledProcessError(
            proc.returncode,
            args,
            output=stdout,
            stderr=stderr,
        )

    return stdout, stderr


async def asyncio_subprocess_check_call(
        *args: str,
        stdout: ta.Any = sys.stderr,
        input: ta.Any = None,  # noqa
        timeout: ta.Optional[float] = None,
        **kwargs: ta.Any,
) -> None:
    _, _ = await _asyncio_subprocess_check_run(
        *args,
        stdout=stdout,
        input=input,
        timeout=timeout,
        **kwargs,
    )


async def asyncio_subprocess_check_output(
        *args: str,
        input: ta.Any = None,  # noqa
        timeout: ta.Optional[float] = None,
        **kwargs: ta.Any,
) -> bytes:
    stdout, stderr = await _asyncio_subprocess_check_run(
        *args,
        stdout=asyncio.subprocess.PIPE,
        input=input,
        timeout=timeout,
        **kwargs,
    )

    return check_not_none(stdout)


async def asyncio_subprocess_check_output_str(*args: str, **kwargs: ta.Any) -> str:
    return (await asyncio_subprocess_check_output(*args, **kwargs)).decode().strip()


##


async def _asyncio_subprocess_try_run(
        fn: ta.Callable[..., ta.Awaitable[T]],
        *args: ta.Any,
        try_exceptions: ta.Tuple[ta.Type[Exception], ...] = DEFAULT_SUBPROCESS_TRY_EXCEPTIONS,
        **kwargs: ta.Any,
) -> ta.Union[T, Exception]:
    try:
        return await fn(*args, **kwargs)
    except try_exceptions as e:  # noqa
        if log.isEnabledFor(logging.DEBUG):
            log.exception('command failed')
        return e


async def asyncio_subprocess_try_call(
        *args: str,
        try_exceptions: ta.Tuple[ta.Type[Exception], ...] = DEFAULT_SUBPROCESS_TRY_EXCEPTIONS,
        **kwargs: ta.Any,
) -> bool:
    if isinstance(await _asyncio_subprocess_try_run(
            asyncio_subprocess_check_call,
            *args,
            try_exceptions=try_exceptions,
            **kwargs,
    ), Exception):
        return False
    else:
        return True


async def asyncio_subprocess_try_output(
        *args: str,
        try_exceptions: ta.Tuple[ta.Type[Exception], ...] = DEFAULT_SUBPROCESS_TRY_EXCEPTIONS,
        **kwargs: ta.Any,
) -> ta.Optional[bytes]:
    if isinstance(ret := await _asyncio_subprocess_try_run(
            asyncio_subprocess_check_output,
            *args,
            try_exceptions=try_exceptions,
            **kwargs,
    ), Exception):
        return None
    else:
        return ret


async def asyncio_subprocess_try_output_str(*args: str, **kwargs: ta.Any) -> ta.Optional[str]:
    out = await asyncio_subprocess_try_output(*args, **kwargs)
    return out.decode().strip() if out is not None else None
