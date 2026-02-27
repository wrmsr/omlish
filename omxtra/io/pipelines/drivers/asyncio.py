# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
"""
TODO:
 - better driver impl
   - only ever call create_task at startup, never in inner loops
     - nothing ever does `asyncio.wait(...)`
   - dedicated read_task, flush_task, sched_task
     - read_task toggles back and forth between reading and waiting
   - main task only reads from command queue
"""
import abc
import asyncio
import dataclasses as dc
import functools
import typing as ta

from omlish.io.streams.utils import ByteStreamBuffers
from omlish.lite.abstract import Abstract
from omlish.lite.check import check
from omlish.logs.modules import get_module_loggers
from omlish.logs.utils import async_exception_logging

from ..asyncs import AsyncChannelPipelineMessages
from ..core import ChannelPipelineHandlerRef
from ..core import ChannelPipelineMessages
from ..core import PipelineChannel
from ..flow.types import ChannelPipelineFlow
from ..flow.types import ChannelPipelineFlowMessages
from ..sched.types import ChannelPipelineScheduling


log, alog = get_module_loggers(globals())  # noqa


##


class AsyncioStreamPipelineChannelDriver(Abstract):
    @dc.dataclass(frozen=True)
    class Config:
        DEFAULT: ta.ClassVar['AsyncioStreamPipelineChannelDriver.Config']

        read_chunk_size: int = 0x10000
        write_chunk_max: ta.Optional[int] = None

    Config.DEFAULT = Config()

    #

    def __init__(
            self,
            spec: PipelineChannel.Spec,
            reader: asyncio.StreamReader,
            writer: ta.Optional[asyncio.StreamWriter] = None,
            config: ta.Optional[Config] = None,
            *,
            on_non_bytes_output: ta.Optional[ta.Callable[[ta.Any], ta.Awaitable[None]]] = None,
    ) -> None:
        super().__init__()

        self._spec = spec
        self._reader = reader
        self._writer = writer
        if config is None:
            config = AsyncioStreamPipelineChannelDriver.Config.DEFAULT
        self._config = config

        self._on_non_bytes_output = on_non_bytes_output

        #

        self._shutdown_event = asyncio.Event()

        self._command_queue: asyncio.Queue[AsyncioStreamPipelineChannelDriver._Command] = asyncio.Queue()

    def __repr__(self) -> str:
        return f'{type(self).__name__}@{id(self):x}'

    @property
    def config(self) -> Config:
        return self._config

    @property
    def channel(self) -> PipelineChannel:
        return self._channel

    ##
    # init

    _sched: 'AsyncioStreamPipelineChannelDriver._Scheduling'

    _channel: PipelineChannel

    _flow: ta.Optional[ChannelPipelineFlow]

    _command_handlers: ta.Mapping[ta.Type['AsyncioStreamPipelineChannelDriver._Command'], ta.Callable[[ta.Any], ta.Awaitable[None]]]  # noqa
    _output_handlers: ta.Mapping[type, ta.Callable[[ta.Any], ta.Awaitable[None]]]

    async def _init(self) -> None:
        self._sched = self._Scheduling(self)

        services = PipelineChannel.Services.of(self._spec.services)
        self._flow = services.find(ChannelPipelineFlow)

        self._command_handlers = self._build_command_handlers()
        self._output_handlers = self._build_output_handlers()

        #

        self._channel = PipelineChannel(dc.replace(
            self._spec,
            services=(*self._spec.services, self._sched),
        ))

    ##
    # async utils

    @staticmethod
    async def _cancel_tasks(
            *tasks: ta.Optional[asyncio.Task],
            check_running: bool = False,
    ) -> None:
        if check_running:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                return
            else:
                if not loop.is_running():
                    return

        #

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

    ##

    class _Command(Abstract):
        pass

    ##
    # feed in

    @dc.dataclass(frozen=True)
    class _FeedInCommand(_Command):
        msgs: ta.Sequence[ta.Any]

        def __repr__(self) -> str:
            return f'{self.__class__.__name__}([{", ".join(map(repr, self.msgs))}])'

    async def _handle_command_feed_in(self, cmd: _FeedInCommand) -> None:
        async def _inner() -> None:
            self._channel.feed_in(*cmd.msgs)  # noqa

        await self._do_with_channel(_inner)

    async def feed_in(self, *msgs: ta.Any) -> None:
        check.state(not self._shutdown_event.is_set())

        self._command_queue.put_nowait(AsyncioStreamPipelineChannelDriver._FeedInCommand(msgs))

    ##
    # read completed

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

    _pending_completed_reads: ta.Optional[ta.List[_ReadCompletedCommand]] = None

    async def _handle_command_read_completed(self, cmd: _ReadCompletedCommand) -> None:
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

    ##
    # update want read

    class _UpdateWantReadCommand(_Command):
        pass

    _has_sent_update_want_read_command: bool = False

    async def _send_update_want_read_command(self) -> None:
        if self._has_sent_update_want_read_command:
            return

        self._has_sent_update_want_read_command = True
        await self._command_queue.put(AsyncioStreamPipelineChannelDriver._UpdateWantReadCommand())

    _want_read = True

    _delay_sending_update_want_read_command = False

    async def _set_want_read(self, want_read: bool) -> None:
        if self._want_read == want_read:
            return

        self._want_read = want_read

        if not self._delay_sending_update_want_read_command:
            await self._send_update_want_read_command()

    async def _handle_command_update_want_read(self, cmd: _UpdateWantReadCommand) -> None:
        self._sent_update_want_read_command = False

        if self._want_read:
            if self._pending_completed_reads:
                in_cmd = AsyncioStreamPipelineChannelDriver._ReadCompletedCommand([
                    b
                    for pcr_cmd in self._pending_completed_reads
                    for b in pcr_cmd.data()
                ])
                self._command_queue.put_nowait(in_cmd)
                self._pending_completed_reads = None

            self._ensure_read_task()

    def _maybe_ensure_read_task(self) -> None:
        if (
                self._want_read or
                (self._flow is not None and self._flow.is_auto_read())
        ):
            self._ensure_read_task()

    @abc.abstractmethod
    def _ensure_read_task(self) -> None:
        raise NotImplementedError

    ##
    # scheduling

    class _Scheduling(ChannelPipelineScheduling):
        def __init__(self, d: 'AsyncioStreamPipelineChannelDriver') -> None:
            super().__init__()

            self._d = d

            self._pending: ta.List[ta.Tuple[float, ta.Callable[[], None]]] = []
            self._tasks: ta.Set[asyncio.Task] = set()

        class _Handle(ChannelPipelineScheduling.Handle):
            def cancel(self) -> None:
                raise NotImplementedError

        def schedule(
                self,
                handler_ref: ChannelPipelineHandlerRef,
                delay_s: float,
                fn: ta.Callable[[], None],
        ) -> ChannelPipelineScheduling.Handle:
            self._pending.append((delay_s, fn))
            return self._Handle()

        def cancel_all(self, handler_ref: ta.Optional[ChannelPipelineHandlerRef] = None) -> None:
            raise NotImplementedError

        async def _task_body(self, delay: float, fn: ta.Callable[[], None]) -> None:
            await asyncio.sleep(delay)

            self._d._command_queue.put_nowait(AsyncioStreamPipelineChannelDriver._ScheduledCommand(fn))  # noqa

        async def _flush_pending(self) -> None:
            if not (lst := self._pending):
                return

            for delay, fn in lst:
                self._tasks.add(asyncio.create_task(functools.partial(self._task_body, delay, fn)()))

            self._pending = []

    @dc.dataclass(frozen=True)
    class _ScheduledCommand(_Command):
        fn: ta.Callable[[], None]

    async def _handle_scheduled_command(self, cmd: _ScheduledCommand) -> None:
        async def _inner() -> None:
            with self._channel.enter():
                cmd.fn()

        await self._do_with_channel(_inner)

    # handlers

    def _build_command_handlers(self) -> ta.Mapping[ta.Type[_Command], ta.Callable[[ta.Any], ta.Awaitable[None]]]:
        return {
            AsyncioStreamPipelineChannelDriver._FeedInCommand: self._handle_command_feed_in,
            AsyncioStreamPipelineChannelDriver._ReadCompletedCommand: self._handle_command_read_completed,
            AsyncioStreamPipelineChannelDriver._UpdateWantReadCommand: self._handle_command_update_want_read,
            AsyncioStreamPipelineChannelDriver._ScheduledCommand: self._handle_scheduled_command,
        }

    async def _handle_command(self, cmd: _Command) -> None:
        try:
            fn = self._command_handlers[cmd.__class__]
        except KeyError:
            raise TypeError(f'Unknown command type: {cmd.__class__}') from None

        await fn(cmd)

    ##
    # output handling

    # lifecycle

    async def _handle_output_final_output(self, msg: ChannelPipelineMessages.FinalOutput) -> None:
        self._shutdown_event.set()

        await self._close_writer()

    # data (special cased)

    async def _handle_output_bytes(self, msg: ta.Any) -> None:
        for mv in ByteStreamBuffers.iter_segments(msg):
            if self._writer is not None and mv:
                self._writer.write(mv)

    # flow

    async def _handle_output_flush_output(self, msg: ChannelPipelineFlowMessages.FlushOutput) -> None:
        if self._writer is not None:
            await self._writer.drain()

    async def _handle_output_ready_for_input(self, msg: ChannelPipelineFlowMessages.ReadyForInput) -> None:
        await self._set_want_read(True)

    # async

    async def _handle_output_await(self, msg: AsyncChannelPipelineMessages.Await) -> None:
        try:
            result = await msg.obj

        except Exception as e:  # noqa
            with self._channel.enter():
                msg.set_failed(e)

        else:
            with self._channel.enter():
                msg.set_succeeded(result)

    # handlers

    def _build_output_handlers(self) -> ta.Mapping[type, ta.Callable[[ta.Any], ta.Awaitable[None]]]:
        return {
            ChannelPipelineMessages.FinalOutput: self._handle_output_final_output,

            ChannelPipelineFlowMessages.FlushOutput: self._handle_output_flush_output,
            ChannelPipelineFlowMessages.ReadyForInput: self._handle_output_ready_for_input,

            AsyncChannelPipelineMessages.Await: self._handle_output_await,
        }

    async def _handle_output(self, msg: ta.Any) -> None:
        if ByteStreamBuffers.can_bytes(msg):
            await self._handle_output_bytes(msg)
            return

        try:
            fn = self._output_handlers[msg.__class__]
        except KeyError:
            raise TypeError(f'Unknown output type: {msg.__class__}') from None

        await fn(msg)

    # execution helpers

    async def _do_with_channel(self, fn: ta.Callable[[], ta.Awaitable[None]]) -> None:
        prev_want_read = self._want_read
        if self._flow is not None and not self._flow.is_auto_read():
            self._want_read = False

        self._delay_sending_update_want_read_command = True
        try:
            await fn()

            await self._drain_channel_output()

        finally:
            self._delay_sending_update_want_read_command = False

        if self._shutdown_event.is_set():
            return

        await self._sched._flush_pending()  # noqa

        if self._want_read != prev_want_read:
            await self._send_update_want_read_command()

        self._maybe_ensure_read_task()

    async def _drain_channel_output(self) -> None:
        while (msg := self._channel.output.poll()) is not None:
            await self._handle_output(msg)

    ##
    # shutdown

    _shutdown_task: asyncio.Task

    async def _shutdown_task_main(self) -> None:
        await self._shutdown_event.wait()

    ##
    # main loop

    @abc.abstractmethod
    def _run(self) -> ta.Awaitable[None]:
        raise NotImplementedError

    @async_exception_logging(alog)
    async def run(self) -> None:
        try:
            self._shutdown_task  # noqa
        except AttributeError:
            pass
        else:
            raise RuntimeError('Already running')

        await self._init()

        self._shutdown_task = asyncio.create_task(self._shutdown_task_main())

        try:
            try:
                await self._run()

            finally:
                self._channel.destroy()

        finally:
            await self._cancel_tasks(self._shutdown_task, check_running=True)


##


class SimpleAsyncioStreamPipelineChannelDriver(AsyncioStreamPipelineChannelDriver):
    _read_task: ta.Optional[asyncio.Task] = None

    def _ensure_read_task(self) -> None:
        if self._read_task is not None or self._shutdown_event.is_set():
            return

        self._read_task = asyncio.create_task(self._reader.read(self._config.read_chunk_size))

        def _done(task: 'asyncio.Task[bytes]') -> None:
            check.state(task is self._read_task)
            self._read_task = None

            if self._shutdown_event.is_set():
                return

            cmd: AsyncioStreamPipelineChannelDriver._Command
            try:
                data = task.result()
            except asyncio.CancelledError:
                cmd = AsyncioStreamPipelineChannelDriver._ReadCancelledCommand()  # noqa
            else:
                cmd = AsyncioStreamPipelineChannelDriver._ReadCompletedCommand(data)  # noqa

            self._command_queue.put_nowait(cmd)

            self._maybe_ensure_read_task()

        self._read_task.add_done_callback(_done)

    #

    async def _run(self) -> None:
        self._ensure_read_task()

        #

        command_queue_task: ta.Optional[asyncio.Task[AsyncioStreamPipelineChannelDriver._Command]] = None

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
            await self._cancel_tasks(
                command_queue_task,
                self._read_task,
                check_running=True,
            )
