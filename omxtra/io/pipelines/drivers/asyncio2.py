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

    class _UpdateWantReadCommand(_Command):
        def __init__(self, pending_data: ta.Optional[bytes] = None) -> None:
            self._pending_data = pending_data

        def __repr__(self) -> str:
            return f'{self.__class__.__name__}@{id(self):x}({"..." if self._pending_data is not None else ""})'

    _want_read = True

    _update_want_read_command: ta.Optional[_UpdateWantReadCommand] = None
    _has_sent_update_want_read_command: bool = False

    async def _set_want_read(self, want_read: bool) -> None:
        if self._want_read == want_read:
            return

        self._want_read = want_read

        if (cmd := self._update_want_read_command) is None:
            cmd = self._update_want_read_command = self._UpdateWantReadCommand()

        if not self._has_sent_update_want_read_command:
            self._has_sent_update_want_read_command = True
            await self._command_queue.put(cmd)

    #

    _driver_task: asyncio.Task

    _command_queue_task: ta.Optional['asyncio.Task[_Command]'] = None
    _read_task: ta.Optional['asyncio.Task[bytes]'] = None

    async def _driver_task_main(self) -> None:
        try:
            while True:
                wait_tasks: ta.List[asyncio.Task] = [self._shutdown_task]

                if self._command_queue_task is None:
                    self._command_queue_task = asyncio.create_task(self._command_queue.get())
                wait_tasks.append(self._command_queue_task)

                if self._want_read:
                    if self._read_task is None:
                        self._read_task = asyncio.create_task(self._reader.read(self._read_chunk_size))
                    wait_tasks.append(self._read_task)
                else:
                    raise NotImplementedError

                done, pending = await asyncio.wait(
                    wait_tasks,
                    return_when=asyncio.FIRST_COMPLETED,
                )

                winner = done.pop()
                if winner is self._shutdown_task:
                    break

                elif winner is self._command_queue_task:
                    cmd = self._command_queue_task.result()
                    self._command_queue_task = None

                    await self._handle_command(cmd)

                    del cmd
                    self._command_queue_task = None

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
            await self._cancel_tasks(self._command_queue_task, self._read_task)

    async def _handle_command(self, cmd: _Command) -> None:
        if isinstance(cmd, AsyncioStreamChannelPipelineDriver2._UpdateWantReadCommand):
            raise NotImplementedError

        else:
            raise TypeError(cmd)

    async def _handle_read(self, data: bytes) -> None:
        check.state(self._want_read)

        if data:
            in_msgs: ta.List[ta.Any] = [data]

            if self._flow is not None:
                in_msgs.append(ChannelPipelineFlowMessages.FlushInput())

            self._channel.feed_in(*in_msgs)

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
                await self._set_want_read(True)

            # other

            elif self._on_non_bytes_output is not None:
                await self._on_non_bytes_output(msg)

    #

    async def run(self) -> None:
        self._shutdown_task = asyncio.create_task(self._shutdown_task_main())
        self._driver_task = asyncio.create_task(self._driver_task_main())

        await self._driver_task

        await self._cancel_tasks(self._shutdown_task)
