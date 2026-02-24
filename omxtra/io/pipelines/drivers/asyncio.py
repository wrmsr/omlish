# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import asyncio
import typing as ta

from omlish.io.streams.utils import ByteStreamBuffers
from omlish.lite.abstract import Abstract
from omlish.lite.check import check
from omlish.logs.modules import get_module_loggers
from omlish.logs.utils import async_exception_logging

from ..core import ChannelPipelineMessages
from ..core import PipelineChannel
from ..flow.types import ChannelPipelineFlow
from ..flow.types import ChannelPipelineFlowMessages


##


log, alog = get_module_loggers(globals())  # noqa


class AsyncioStreamChannelPipelineDriver:
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

        self._command_queue: asyncio.Queue[AsyncioStreamChannelPipelineDriver._Command] = asyncio.Queue()

        self._shutdown_event = asyncio.Event()

    def __repr__(self) -> str:
        return f'{type(self).__name__}@{id(self):x}'

    #

    @staticmethod
    async def _cancel_tasks(*tasks: ta.Optional[asyncio.Task]) -> None:
        cts: ta.List[asyncio.Task] = []

        for t in tasks:
            if t is not None and not t.done():
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

    class _Command(Abstract):
        pass

    #

    class _FeedInCommand(_Command):
        def __init__(self, *msgs: ta.Any) -> None:
            self._msgs = msgs

    async def _handle_feed_in_command(self, cmd: _FeedInCommand) -> None:
        async def _inner() -> None:
            self._channel.feed_in(*cmd._msgs)  # noqa

        await self._do_with_channel(_inner)

    async def feed_in(self, *msgs: ta.Any) -> None:
        check.state(not self._shutdown_event.is_set())

        self._command_queue.put_nowait(AsyncioStreamChannelPipelineDriver._FeedInCommand(*msgs))

    #

    class _ReadCompletedCommand(_Command):
        def __init__(self, data: ta.Union[bytes, ta.List[bytes]]) -> None:
            self._data = data

        def __repr__(self) -> str:
            return (
                f'{self.__class__.__name__}@{id(self):x}'
                f'({"[...]" if isinstance(self._data, list) else "..." if self._data is not None else ""})'
            )

        def data(self) -> ta.Sequence[bytes]:
            if isinstance(self._data, bytes):
                return [self._data]
            elif isinstance(self._data, list):
                return self._data
            else:
                raise TypeError(self._data)

    class _ReadCancelledCommand(_Command):
        pass

    _read_task: ta.Optional[asyncio.Task] = None

    def _ensure_read_task(self) -> None:
        if self._read_task is not None or self._shutdown_event.is_set():
            return

        self._read_task = asyncio.create_task(self._reader.read(self._read_chunk_size))

        def _done(task: 'asyncio.Task[bytes]') -> None:
            check.state(task is self._read_task)
            self._read_task = None

            if self._shutdown_event.is_set():
                return

            cmd: AsyncioStreamChannelPipelineDriver._Command
            try:
                data = task.result()
            except asyncio.CancelledError:
                cmd = AsyncioStreamChannelPipelineDriver._ReadCancelledCommand()
            else:
                cmd = AsyncioStreamChannelPipelineDriver._ReadCompletedCommand(data)

            self._command_queue.put_nowait(cmd)

            self._maybe_ensure_read_task()

        self._read_task.add_done_callback(_done)

    def _maybe_ensure_read_task(self) -> None:
        if (
                self._want_read or
                (self._flow is not None and self._flow.is_auto_read())
        ):
            self._ensure_read_task()

    _pending_completed_reads: ta.Optional[ta.List[_ReadCompletedCommand]] = None

    async def _handle_read_completed_command(self, cmd: _ReadCompletedCommand) -> None:
        if not self._want_read:
            if (pl := self._pending_completed_reads) is None:
                pl = self._pending_completed_reads = []

            pl.append(cmd)
            return

        #

        eof = False

        in_msgs: ta.List[ta.Any] = []

        for b in cmd.data():
            check.state(not eof)
            if not b:
                eof = True
            else:
                in_msgs.append(b)

        if self._flow is not None:
            in_msgs.append(ChannelPipelineFlowMessages.FlushInput())

        if eof:
            in_msgs.append(ChannelPipelineMessages.FinalInput())

        #

        async def _inner() -> None:
            self._channel.feed_in(*in_msgs)

        await self._do_with_channel(_inner)

        #

        if eof:
            self._shutdown_event.set()

            await self._close_writer()

    #

    class _UpdateWantReadCommand(_Command):
        pass

    _has_sent_update_want_read_command: bool = False

    async def _send_update_want_read_command(self) -> None:
        if self._has_sent_update_want_read_command:
            return

        self._has_sent_update_want_read_command = True
        await self._command_queue.put(AsyncioStreamChannelPipelineDriver._UpdateWantReadCommand())

    _want_read = True

    _delay_sending_update_want_read_command = False

    async def _set_want_read(self, want_read: bool) -> None:
        if self._want_read == want_read:
            return

        self._want_read = want_read

        if not self._delay_sending_update_want_read_command:
            await self._send_update_want_read_command()

    async def _handle_update_want_read_command(self, cmd: _UpdateWantReadCommand) -> None:
        self._sent_update_want_read_command = False

        if self._want_read:
            if self._pending_completed_reads:
                in_cmd = AsyncioStreamChannelPipelineDriver._ReadCompletedCommand([
                    b
                    for pcr_cmd in self._pending_completed_reads
                    for b in pcr_cmd.data()
                ])
                self._command_queue.put_nowait(in_cmd)
                self._pending_completed_reads = None

            self._ensure_read_task()

    async def _handle_command(self, cmd: _Command) -> None:
        if isinstance(cmd, AsyncioStreamChannelPipelineDriver._FeedInCommand):
            await self._handle_feed_in_command(cmd)

        elif isinstance(cmd, AsyncioStreamChannelPipelineDriver._ReadCompletedCommand):
            await self._handle_read_completed_command(cmd)

        elif isinstance(cmd, AsyncioStreamChannelPipelineDriver._UpdateWantReadCommand):
            await self._handle_update_want_read_command(cmd)

        else:
            raise TypeError(cmd)

    #

    async def _do_with_channel(self, fn: ta.Callable[[], ta.Awaitable[None]]) -> None:
        prev_want_read = self._want_read
        if self._flow is not None and not self._flow.is_auto_read():
            self._want_read = False

        self._delay_sending_update_want_read_command = True
        try:
            await fn()

            await self._drain_channel()

        finally:
            self._delay_sending_update_want_read_command = False

        if self._shutdown_event.is_set():
            return

        if self._want_read != prev_want_read:
            await self._send_update_want_read_command()

        self._maybe_ensure_read_task()

    #

    async def _drain_channel(self) -> None:
        for msg in self._channel.drain():
            # data

            if ByteStreamBuffers.can_bytes(msg):
                for mv in ByteStreamBuffers.iter_segments(msg):
                    if self._writer is not None and mv:
                        self._writer.write(mv)

            elif isinstance(msg, ChannelPipelineMessages.FinalOutput):
                self._shutdown_event.set()

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

    _shutdown_task: asyncio.Task

    async def _shutdown_task_main(self) -> None:
        await self._shutdown_event.wait()

    #

    async def _run(self) -> None:
        try:
            self._shutdown_task  # noqa
        except AttributeError:
            pass
        else:
            raise RuntimeError('Already running')
        self._shutdown_task = asyncio.create_task(self._shutdown_task_main())

        #

        self._ensure_read_task()

        #

        command_queue_task: ta.Optional[asyncio.Task[AsyncioStreamChannelPipelineDriver._Command]] = None

        try:
            while not self._shutdown_event.is_set():
                if command_queue_task is None:
                    command_queue_task = asyncio.create_task(self._command_queue.get())

                done, pending = await asyncio.wait(
                    [command_queue_task, self._shutdown_task],
                    return_when=asyncio.FIRST_COMPLETED,
                )

                winner = done.pop()

                if self._shutdown_event.is_set() or winner is self._shutdown_task:
                    break

                elif winner is command_queue_task:
                    cmd = command_queue_task.result()
                    command_queue_task = None

                    await self._handle_command(cmd)

                    del cmd
                    command_queue_task = None

                else:
                    raise RuntimeError(f'Unexpected task: {winner!r}')
        #

        finally:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                pass
            else:
                if loop.is_running():
                    await self._cancel_tasks(
                        command_queue_task,
                        self._shutdown_task,
                        self._read_task,
                    )

    @async_exception_logging(alog)
    async def run(self) -> None:
        await self._run()
