import sys
import asyncio
import typing as ta


ASYNCIO_DEFAULT_BUFFER_LIMIT = 2 ** 16


async def asyncio_open_stream_reader(
        f: ta.IO,
        loop: ta.Optional[asyncio.BaseEventLoop] = None,
        *,
        limit: int = ASYNCIO_DEFAULT_BUFFER_LIMIT,
) -> asyncio.StreamReader:
    if loop is None:
        loop = asyncio.get_event_loop()

    reader = asyncio.StreamReader(limit=limit, loop=loop)
    await loop.connect_read_pipe(
        lambda: asyncio.StreamReaderProtocol(reader, loop=loop),
        f,
    )

    return reader


async def asyncio_open_stream_writer(
        f: ta.IO,
        loop: ta.Optional[asyncio.BaseEventLoop] = None,
) -> asyncio.StreamWriter:
    if loop is None:
        loop = asyncio.get_event_loop()

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


async def _a_main() -> None:
    stdin = await asyncio_open_stream_reader(sys.stdin)
    stdout = await asyncio_open_stream_writer(sys.stdout)

    stdout.write(b'hi!\n')
    await stdout.drain()

    print(await stdin.readline())


if __name__ == '__main__':
    asyncio.run(_a_main())
