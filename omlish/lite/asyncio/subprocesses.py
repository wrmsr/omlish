# ruff: noqa: UP006 UP007
import asyncio.base_subprocess
import asyncio.subprocess
import contextlib
import functools
import logging
import subprocess
import typing as ta

from ..check import check_equal
from ..check import check_isinstance
from ..check import check_not_none
from ..check import check_single
from ..logs import log
from ..subprocesses import DEFAULT_SUBPROCESS_TRY_EXCEPTIONS
from ..subprocesses import prepare_subprocess_invocation
from .asyncio import asyncio_maybe_timeout


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
        if self._proc.stdin is not None:
            stdin = self._feed_stdin(input)
        else:
            stdin = self._noop()

        if self._proc.stdout is not None:
            stdout = self._read_stream(1)
        else:
            stdout = self._noop()

        if self._proc.stderr is not None:
            stderr = self._read_stream(2)
        else:
            stderr = self._noop()

        # Need to 'tuple' this to work around a mypy bug:
        # File "mypy/checker.py", line 3911, in check_multi_assignment_from_tuple
        #   assert isinstance(reinferred_rvalue_type, TupleType)
        # AssertionError:
        # (Pdb) pp reinferred_rvalue_type
        # builtins.list[Union[builtins.bytes, None]]
        stdin, stdout, stderr = tuple(await asyncio.gather(stdin, stdout, stderr))

        await self._proc.wait()

        return AsyncioProcessCommunicator.Communication(stdout, stderr)

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
    return await AsyncioProcessCommunicator(proc).communicate(input, timeout)  # type: ignore


##


# async def asyncio_subprocess_check_call(
#         *args: str,
#         stdout: ta.Any = 'stderr',
#         input: ta.Any = None,  # noqa
#         timeout: ta.Optional[float] = None,
#         **kwargs: ta.Any,
# ) -> None:
#     args, kwargs = prepare_subprocess_invocation(*args, **kwargs)
#
#     proc: asyncio.subprocess.Process
#     async with asyncio_subprocess_popen(
#             *args,
#             stdout=stdout,
#             **kwargs,
#     ) as proc:
#         stdout, stderr = await asyncio_subprocess_communicate(proc, input, timeout)
#
#     if proc.returncode:
#         raise subprocess.CalledProcessError(
#             proc.returncode,
#             args,
#             output=stdout,
#             stderr=stderr,
#         )


async def asyncio_subprocess_check_output(
        *args: str,
        input: ta.Any = None,  # noqa
        timeout: ta.Optional[float] = None,
        **kwargs: ta.Any,
) -> bytes:
    args, kwargs = prepare_subprocess_invocation(*args, **kwargs)

    proc: asyncio.subprocess.Process
    async with asyncio_subprocess_popen(
            *args,
            stdout=asyncio.subprocess.PIPE,
            **kwargs,
    ) as proc:
        stdout, stderr = await asyncio_subprocess_communicate(proc, input, timeout)

    if proc.returncode:
        raise subprocess.CalledProcessError(
            proc.returncode,
            args,
            output=stdout,
            stderr=stderr,
        )

    return check_not_none(stdout)


async def asyncio_subprocess_check_output_str(*args: str, **kwargs: ta.Any) -> str:
    return (await asyncio_subprocess_check_output(*args, **kwargs)).decode().strip()


##


async def asyncio_subprocess_try_output(
        *args: str,
        try_exceptions: ta.Tuple[ta.Type[Exception], ...] = DEFAULT_SUBPROCESS_TRY_EXCEPTIONS,
        **kwargs: ta.Any,
) -> ta.Optional[bytes]:
    try:
        return await asyncio_subprocess_check_output(*args, **kwargs)
    except try_exceptions as e:  # noqa
        if log.isEnabledFor(logging.DEBUG):
            log.exception('command failed')
        return None


async def asyncio_subprocess_try_output_str(*args: str, **kwargs: ta.Any) -> ta.Optional[str]:
    out = await asyncio_subprocess_try_output(*args, **kwargs)
    return out.decode().strip() if out is not None else None
