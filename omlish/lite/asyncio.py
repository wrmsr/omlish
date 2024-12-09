# ruff: noqa: UP006 UP007
import asyncio.subprocess
import contextlib
import functools
import typing as ta

from .check import check_single


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
