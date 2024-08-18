# -*- coding: utf-8 -*-


import asyncio

from asyncio import AbstractEventLoop, StreamReader, StreamWriter
from typing import Iterable, Optional, Tuple


_DEFAULT_LIMIT = 2 ** 16


class _MemoryTransport(asyncio.Transport):
    """Direct connection between a StreamWriter and StreamReader."""

    def __init__(self, reader: StreamReader) -> None:
        super().__init__()
        self._reader = reader

    def write(self, data: bytes) -> None:
        self._reader.feed_data(data)

    def writelines(self, data: Iterable[bytes]) -> None:
        for line in data:
            self._reader.feed_data(line)
            self._reader.feed_data(b'\n')

    def write_eof(self) -> None:
        self._reader.feed_eof()

    def can_write_eof(self) -> bool:
        return True

    def is_closing(self) -> bool:
        return False

    def close(self) -> None:
        self.write_eof()


def mempipe(
        loop: Optional[AbstractEventLoop]=None,
        limit: int=None,
) -> Tuple[StreamReader, StreamWriter]:
    """In-memory pipe, returns a ``(reader, writer)`` pair.

    .. versionadded:: 0.1

    """

    loop = loop or asyncio.get_event_loop()
    limit = limit or _DEFAULT_LIMIT

    reader = asyncio.StreamReader(loop=loop, limit=limit)  # type: StreamReader
    writer = asyncio.StreamWriter(
        transport=_MemoryTransport(reader),
        protocol=asyncio.StreamReaderProtocol(reader, loop=loop),
        reader=reader,
        loop=loop,
    )  # type: StreamWriter
    return reader, writer
