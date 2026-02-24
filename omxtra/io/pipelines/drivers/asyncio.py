# ruff: noqa: UP045
# @omlish-lite
import asyncio
import typing as ta

from omlish.io.streams.utils import ByteStreamBuffers

from ..core import PipelineChannel
from ..flow.types import ChannelPipelineFlow


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

        self._flow = channel.services.find(ChannelPipelineFlow)

    async def run(self) -> None:
        try:
            while True:
                action = await self._run_one()

                if action == 'return':
                    break
                elif action == 'continue':
                    continue
                else:
                    raise RuntimeError(f'Unknown action: {action!r}')  # noqa

        except BaseException as e:  # noqa
            # # FIXME: internal.. some kinda ChannelDriver interface? ChannelDriverContext?
            # self._channel._handle_error(e)  # noqa

            await self._flush_channel()
            await self._close_writer()

    async def _run_one(self) -> ta.Literal['continue', 'return']:
        # Always flush outbound first; helps drain after handler writes.
        await self._flush_channel()

        # If channel closed, flush outbound and close transport.
        if self._channel.saw_final_output:  # intentionally internal; this is the edge driver
            await self._flush_channel()
            await self._close_writer()
            return 'return'

        await self._gate_inbound()

        if self._channel.saw_final_output:
            return 'continue'  # type: ignore[unreachable]  # FIXME: ??

        data = await self._reader.read(self._read_chunk_size)
        if not data:
            self._channel.feed_final_input()
            await self._flush_channel()
            await self._close_writer()
            return 'return'

        self._channel.feed_in(data)
        return 'continue'

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
