# ruff: noqa: UP045
# @omlish-lite
import asyncio
import typing as ta

from omlish.io.streams.utils import ByteStreamBuffers
from omlish.lite.check import check

from .bytes import BytesChannelPipelineFlowControl
from .core import PipelineChannel


##


class AsyncioStreamChannelPipelineDriver:
    def __init__(
            self,
            channel: PipelineChannel,
            reader: asyncio.StreamReader,
            writer: ta.Optional[asyncio.StreamWriter] = None,
            *,
            read_chunk_size: int = 0x10000,
            write_chunk_max: ta.Optional[int] = None,

            on_app_msg: ta.Optional[ta.Callable[[ta.Any], None]] = None,
    ) -> None:
        super().__init__()

        self._channel = channel
        self._reader = reader
        self._writer = writer

        self._read_chunk_size = read_chunk_size
        self._write_chunk_max = write_chunk_max

        self._on_app_msg = on_app_msg

    async def run(self) -> None:
        try:
            while True:
                # Always flush outbound first; helps drain after handler writes.
                await self._flush_channel()

                # If channel closed, flush outbound and close transport.
                if self._channel.closed:  # intentionally internal; this is the edge driver
                    await self._flush_channel()
                    await self._close_writer()
                    return

                await self._gate_inbound()

                if self._channel.closed:
                    continue  # type: ignore[unreachable]  # FIXME: ??

                data = await self._reader.read(self._read_chunk_size)
                if not data:
                    self._channel.feed_eof()
                    await self._flush_channel()
                    await self._close_writer()
                    return

                self._channel.feed_in(data)

        except BaseException as e:  # noqa
            self._channel.handle_error(e)

            await self._flush_channel()
            await self._close_writer()

    async def _gate_inbound(self) -> None:
        pass

    async def _flush_channel(self) -> None:
        for m in self._channel.drain():
            if ByteStreamBuffers.can_bytes(m):
                for mv in ByteStreamBuffers.iter_segments(m):
                    if self._writer is not None and mv:
                        self._writer.write(mv)

            elif self._on_app_msg is not None:
                self._on_app_msg(m)

    async def _close_writer(self) -> None:
        if self._writer is None:
            return

        try:
            self._writer.close()
            await self._writer.wait_closed()

        except Exception:  # noqa
            # Best effort; transport close errors aren't actionable at this layer.
            pass


class BytesFlowControlAsyncioStreamChannelPipelineDriver(AsyncioStreamChannelPipelineDriver):
    def __init__(
            self,
            channel: PipelineChannel,
            reader: asyncio.StreamReader,
            writer: ta.Optional[asyncio.StreamWriter] = None,
            *,
            read_chunk_size: int = 0x10000,
            write_chunk_max: ta.Optional[int] = None,

            on_app_msg: ta.Optional[ta.Callable[[ta.Any], None]] = None,

            backpressure_sleep: float = 0.,
    ) -> None:
        super().__init__(
            channel,
            reader,
            writer,

            read_chunk_size=read_chunk_size,
            write_chunk_max=write_chunk_max,

            on_app_msg=on_app_msg,
        )

        self._backpressure_sleep = backpressure_sleep

        self._flow = check.not_none(self._channel.pipeline.find_single_handler_of_type(BytesChannelPipelineFlowControl)).handler  # type: ignore[type-abstract]  # noqa

    async def _gate_inbound(self) -> None:
        while not self._flow.want_read():
            await self._flush_channel()

            await asyncio.sleep(self._backpressure_sleep)  # FIXME: lol - event-driven or callback?

            if self._channel.closed:
                break

    async def _flush_channel(self) -> None:
        await self._flush_outbound()

        if self._on_app_msg is not None:
            for m in self._channel.drain():
                self._on_app_msg(m)

        else:
            # Drain to avoid unbounded app queue in examples that don't consume it.
            self._channel.drain()

    async def _flush_outbound(self) -> None:
        if self._writer is None:
            return

        out = self._flow.drain_outbound(self._write_chunk_max)

        for msg in out:
            for mv in ByteStreamBuffers.iter_segments(msg):
                if mv:
                    self._writer.write(mv)

        if out:
            await self._writer.drain()
