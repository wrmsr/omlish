# ruff: noqa: UP006 UP007
import asyncio.subprocess
import contextlib
import functools
import subprocess
import typing as ta

from .check import check_not_none
from .check import check_single
from .subprocesses import prepare_subprocess_invocation


##


ASYNCIO_DEFAULT_BUFFER_LIMIT = 2 ** 16


async def asyncio_open_stream_reader(
        f: ta.IO,
        loop: ta.Any = None,
        *,
        limit: int = ASYNCIO_DEFAULT_BUFFER_LIMIT,
) -> asyncio.StreamReader:
    if loop is None:
        loop = asyncio.get_running_loop()

    reader = asyncio.StreamReader(limit=limit, loop=loop)
    await loop.connect_read_pipe(
        lambda: asyncio.StreamReaderProtocol(reader, loop=loop),
        f,
    )

    return reader


async def asyncio_open_stream_writer(
        f: ta.IO,
        loop: ta.Any = None,
) -> asyncio.StreamWriter:
    if loop is None:
        loop = asyncio.get_running_loop()

    writer_transport, writer_protocol = await loop.connect_write_pipe(
        lambda: asyncio.streams.FlowControlMixin(loop=loop),
        f,
    )

    return asyncio.streams.StreamWriter(
        writer_transport,
        writer_protocol,
        None,
        loop,
    )


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
        if timeout:
            await asyncio.wait_for(proc.wait(), timeout=timeout)
        else:
            await proc.wait()


async def asyncio_subprocess_communicate(
        proc: asyncio.subprocess.Process,
        input: ta.Any = None,  # noqa
        timeout: ta.Optional[float] = None,
) -> ta.Tuple[ta.Optional[bytes], ta.Optional[bytes]]:
    fn: ta.Any = proc.communicate(input)
    if timeout is not None:
        fn = asyncio.wait_for(fn, timeout)
    stdout, stderr = await fn
    return stdout, stderr


#


# async def asyncio_subprocess_check_call(*args: str, stdout=sys.stderr, **kwargs: ta.Any) -> None:
#     args, kwargs = prepare_subprocess_invocation(*args, stdout=stdout, **kwargs)
#     return subprocess.check_call(args, **kwargs)  # type: ignore


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
        stdout, stderr = await asyncio_subprocess_communicate(input, timeout)

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
