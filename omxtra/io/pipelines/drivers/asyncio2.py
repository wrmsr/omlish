# ruff: noqa: UP006 UP045
# @omlish-lite
import asyncio
import typing as ta

from omlish.io.streams.utils import ByteStreamBuffers
from omlish.lite.abstract import Abstract
from omlish.lite.check import check

from ..core import ChannelPipelineMessages
from ..core import PipelineChannel
from ..flow.types import ChannelPipelineFlow
from ..flow.types import ChannelPipelineFlowMessages


##


class AsyncioStreamChannelPipelineDriver2:
    def __init__(
            self,
            channel: PipelineChannel,
            reader: asyncio.StreamReader,
            writer: ta.Optional[asyncio.StreamWriter] = None,
            *,
            read_chunk_size: int = 0x10000,
            write_chunk_max: ta.Optional[int] = None,

            on_non_bytes_output: ta.Optional[ta.Callable[[ta.Any], ta.Awaitable[None]]] = None,
    ) -> None:
        super().__init__()

        self._channel = channel
        self._reader = reader
        self._writer = writer

        self._read_chunk_size = read_chunk_size
        self._write_chunk_max = write_chunk_max

        self._on_non_bytes_output = on_non_bytes_output

        #

        self._flow = channel.services.find(ChannelPipelineFlow)

        #

        self._command_queue: asyncio.Queue[AsyncioStreamChannelPipelineDriver2._Command] = asyncio.Queue()

        self._shutdown_event = asyncio.Event()

        self._want_read = True

    #

    @staticmethod
    async def _cancel_tasks(*tasks: ta.Optional[asyncio.Task]) -> None:
        cts: ta.List[asyncio.Task] = []

        for t in tasks:
            if t is not None:
                t.cancel()
                cts.append(t)

        if cts:
            await asyncio.gather(*cts, return_exceptions=True)

    #

    async def _close_writer(self) -> None:
        if self._writer is None:
            return

        try:
            self._writer.close()
            await self._writer.wait_closed()

        except Exception:  # noqa
            # Best effort; transport close errors aren't actionable at this layer.
            pass

        self._writer = None

    #

    _shutdown_task: asyncio.Task

    async def _shutdown_task_main(self) -> None:
        await self._shutdown_event.wait()

    #

    class _Command(Abstract):
        pass

    #

    _driver_task: asyncio.Task

    _command_task: ta.Optional['asyncio.Task[_Command]'] = None
    _read_task: ta.Optional['asyncio.Task[bytes]'] = None

    async def _driver_task_main(self) -> None:
        try:
            while True:
                wait_tasks: ta.List[asyncio.Task] = [self._shutdown_task]

                if self._command_task is None:
                    self._command_task = asyncio.create_task(self._command_queue.get())
                wait_tasks.append(self._command_task)

                if self._want_read:
                    if self._read_task is None:
                        self._read_task = asyncio.create_task(self._reader.read(self._read_chunk_size))
                    wait_tasks.append(self._read_task)
                else:
                    # FIXME: cancel lol
                    check.none(self._read_task)
                    raise NotImplementedError

                done, pending = await asyncio.wait(
                    wait_tasks,
                    return_when=asyncio.FIRST_COMPLETED,
                )

                winner = done.pop()
                if winner is self._shutdown_task:
                    break

                elif winner is self._command_task:
                    cmd = self._command_task.result()
                    self._command_task = None

                    await self._handle_command(cmd)

                    del cmd
                    self._command_task = None

                elif winner is self._read_task:
                    data = self._read_task.result()
                    self._read_task = None

                    await self._handle_read(data)

                    if not data:
                        break

                    del data

                else:
                    raise RuntimeError(f'Unexpected task: {winner!r}')

        finally:
            await self._cancel_tasks(self._command_task, self._read_task)

    async def _handle_command(self, cmd: _Command) -> None:
        raise NotImplementedError

    async def _handle_read(self, data: bytes) -> None:
        if data:
            self._channel.feed_in(data)
        else:
            self._channel.feed_final_input()

        await self._drain_channel()

        if not data:
            self._shutdown_event.set()

            await self._close_writer()

    #

    async def _drain_channel(self) -> None:
        for msg in self._channel.drain():
            # data

            if ByteStreamBuffers.can_bytes(msg):
                for mv in ByteStreamBuffers.iter_segments(msg):
                    if self._writer is not None and mv:
                        self._writer.write(mv)

            elif isinstance(msg, ChannelPipelineMessages.FinalOutput):
                await self._close_writer()

            # flow

            elif isinstance(msg, ChannelPipelineFlowMessages.FlushOutput):
                if self._writer is not None:
                    await self._writer.drain()

            elif isinstance(msg, ChannelPipelineFlowMessages.ReadyForInput):
                self._want_read = True
                raise NotImplementedError

            # other

            elif self._on_non_bytes_output is not None:
                await self._on_non_bytes_output(msg)

    #

    async def run(self) -> None:
        self._shutdown_task = asyncio.create_task(self._shutdown_task_main())
        self._driver_task = asyncio.create_task(self._driver_task_main())

        await self._driver_task

        await self._cancel_tasks(self._shutdown_task)
