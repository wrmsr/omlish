# ruff: noqa: UP006 UP007
# @omlish-lite
import asyncio
import typing as ta


##


class AsyncioBytesChannelTransport(asyncio.Transport):
    def __init__(self, reader: asyncio.StreamReader) -> None:
        super().__init__()

        self.reader = reader
        self.closed: asyncio.Future = asyncio.Future()

    # @ta.override
    def write(self, data: bytes) -> None:
        self.reader.feed_data(data)

    # @ta.override
    def close(self) -> None:
        self.reader.feed_eof()
        if not self.closed.done():
            self.closed.set_result(True)

    # @ta.override
    def is_closing(self) -> bool:
        return self.closed.done()


def asyncio_create_bytes_channel(
        loop: ta.Any = None,
) -> ta.Tuple[asyncio.StreamReader, asyncio.StreamWriter]:
    if loop is None:
        loop = asyncio.get_running_loop()

    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    transport = AsyncioBytesChannelTransport(reader)
    writer = asyncio.StreamWriter(transport, protocol, reader, loop)

    return reader, writer
