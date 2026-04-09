# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import asyncio
import dataclasses as dc
import functools
import typing as ta

from ....lite.abstract import Abstract
from ....lite.check import check
from ....logs.modules import get_module_loggers
from ....logs.utils import async_exception_logging
from ...streams.utils import ByteStreamBuffers
from ..asyncs import AsyncIoPipelineMessages
from ..core import IoPipeline
from ..core import IoPipelineHandlerRef
from ..core import IoPipelineMessages
from ..core import IoPipelineService
from ..core import IoPipelineServices
from ..flow.types import IoPipelineFlow
from ..flow.types import IoPipelineFlowMessages
from ..sched.types import IoPipelineScheduling
from .metadata import DriverIoPipelineMetadata


log, alog = get_module_loggers(globals())  # noqa


##


class PollAsyncioStreamIoPipelineDriver:
    """
    An asyncio pipeline driver with a poll-based interface mirroring the sync driver's API. Unlike
    LoopAsyncioStreamIoPipelineDriver which runs its own internal event loop via run(), this driver exposes next() and
    loop_until_done() methods that let the caller control stepping. Unhandled pipeline output messages are returned from
    next(), enabling streaming use cases.
    """

    @dc.dataclass(frozen=True)
    class Config:
        DEFAULT: ta.ClassVar['PollAsyncioStreamIoPipelineDriver.Config']

        read_chunk_size: int = 64 * 1024
        write_chunk_max: ta.Optional[int] = None

        strict_input_flow: bool = False

    Config.DEFAULT = Config()

    #

    def __init__(
            self,
            spec: IoPipeline.Spec,
            reader: asyncio.StreamReader,
            writer: ta.Optional[asyncio.StreamWriter] = None,
            config: ta.Optional[Config] = None,
            *,
            _pipeline_kwargs: ta.Optional[ta.Mapping[str, ta.Any]] = None,
    ) -> None:
        super().__init__()

        self._spec = spec
        self._reader = reader
        self._writer = writer
        if config is None:
            config = PollAsyncioStreamIoPipelineDriver.Config.DEFAULT
        self._config = config
        self._pipeline_kwargs = _pipeline_kwargs

        #

        self._shutdown_event = asyncio.Event()
        self._command_queue: asyncio.Queue = asyncio.Queue()

        self._want_read = False
        self._want_read_event = asyncio.Event()

        self._command_queue.put_nowait(PollAsyncioStreamIoPipelineDriver._FeedInCommand([
            IoPipelineMessages.InitialInput(),
        ]))

    def __repr__(self) -> str:
        return f'{type(self).__name__}@{id(self):x}'

    @property
    def config(self) -> Config:
        return self._config

    @property
    def pipeline(self) -> IoPipeline:
        return self._pipeline

    @property
    def is_running(self) -> bool:
        try:
            pipeline = self._pipeline
        except AttributeError:
            return False
        return pipeline.is_ready

    ##
    # init

    _has_init = False

    _sched: 'PollAsyncioStreamIoPipelineDriver._SchedulingService'

    _pipeline: IoPipeline

    _flow: ta.Optional[IoPipelineFlow]

    _command_handlers: ta.Mapping[ta.Type['PollAsyncioStreamIoPipelineDriver._Command'], ta.Callable[[ta.Any], ta.Awaitable[None]]]  # noqa
    _output_handlers: ta.Mapping[type, ta.Callable[[ta.Any], ta.Awaitable[ta.Optional[str]]]]

    async def _ensure_init(self) -> IoPipeline:
        if self._has_init:
            return self._pipeline
        self._has_init = True

        self._sched = self._SchedulingService(self)

        services = IoPipelineServices.of(self._spec.services)
        self._flow = services.find(IoPipelineFlow)

        self._command_handlers = self._build_command_handlers()
        self._output_handlers = self._build_output_handlers()

        #

        self._pipeline = IoPipeline(
            dc.replace(
                self._spec,
                metadata=(*self._spec.metadata, DriverIoPipelineMetadata(self)),
                services=(*self._spec.services, self._sched),
            ),
            **(self._pipeline_kwargs or {}),
        )

        #

        self._read_task = asyncio.create_task(self._read_task_main())

        if self._is_auto_read():
            self._want_read = True
            self._want_read_event.set()

        return self._pipeline

    def _is_auto_read(self) -> bool:
        return (flow := self._flow) is None or flow.is_auto_read()

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

        fut: ta.Optional['asyncio.Future[None]'] = None

        def __repr__(self) -> str:
            return f'{self.__class__.__name__}([{", ".join(map(repr, self.msgs))}])'

    async def _handle_command_feed_in(self, cmd: _FeedInCommand) -> None:
        try:
            self._pipeline.feed_in(*cmd.msgs)

        except BaseException as e:
            if (fut := cmd.fut) is not None:
                fut.set_exception(e)
            raise

        else:
            if (fut := cmd.fut) is not None:
                fut.set_result(None)

    def enqueue_waitable(self, *msgs: ta.Any) -> 'asyncio.Future[None]':
        check.state(not self._shutdown_event.is_set())

        fut: asyncio.Future[None] = asyncio.Future()
        self._command_queue.put_nowait(PollAsyncioStreamIoPipelineDriver._FeedInCommand(msgs, fut=fut))
        return fut

    def enqueue(self, *msgs: ta.Any) -> None:
        check.state(not self._shutdown_event.is_set())

        self._command_queue.put_nowait(PollAsyncioStreamIoPipelineDriver._FeedInCommand(msgs))

    ##
    # read task

    _read_task: ta.Optional[asyncio.Task] = None

    _has_read_eof: bool = False

    async def _read_task_main(self) -> None:
        try:
            while not self._shutdown_event.is_set():
                # In manual flow mode, wait for ReadyForInput to signal via _want_read_event.
                if not self._is_auto_read():
                    await self._want_read_event.wait()

                    if self._shutdown_event.is_set():
                        break

                    self._want_read_event.clear()

                try:
                    data = await self._reader.read(self._config.read_chunk_size)
                except asyncio.CancelledError:
                    raise
                except Exception:  # noqa
                    data = b''

                if self._shutdown_event.is_set():
                    break

                self._command_queue.put_nowait(
                    PollAsyncioStreamIoPipelineDriver._ReadCompletedCommand(data),
                )

                if not data:  # EOF
                    break

        except asyncio.CancelledError:
            pass

    ##
    # read completed

    class _ReadCompletedCommand(_Command):
        def __init__(self, data: ta.Union[bytes, ta.List[bytes]]) -> None:
            self._data = data

        def __repr__(self) -> str:
            return (
                f'{self.__class__.__name__}@{id(self):x}'
                f'({"[...]" if isinstance(self._data, list) else "..." if self._data else ""})'
            )

        def data(self) -> ta.Sequence[bytes]:
            if isinstance(self._data, bytes):
                return [self._data]
            elif isinstance(self._data, list):
                return self._data
            else:
                raise TypeError(self._data)

    async def _handle_command_read_completed(self, cmd: _ReadCompletedCommand) -> None:
        eof = False

        in_msgs: ta.List[ta.Any] = []

        for b in cmd.data():
            check.state(not eof)
            if not b:
                eof = True
            else:
                in_msgs.append(b)

        if not eof and self._flow is not None:
            in_msgs.append(IoPipelineFlowMessages.FlushInput())

        if self._flow is not None:
            self._want_read = False

        if eof:
            self._has_read_eof = True

            in_msgs.append(IoPipelineMessages.FinalInput())

        #

        self._pipeline.feed_in(*in_msgs)

        #

        if eof:
            self._shutdown_event.set()

            await self._close_writer()

    ##
    # scheduling

    class _SchedulingService(IoPipelineScheduling, IoPipelineService):
        def __init__(self, d: 'PollAsyncioStreamIoPipelineDriver') -> None:
            super().__init__()

            self._d = d

            self._pending: ta.List[ta.Tuple[float, ta.Callable[[], None]]] = []
            self._tasks: ta.Set[asyncio.Task] = set()

        class _Handle(IoPipelineScheduling.Handle):
            def cancel(self) -> None:
                raise NotImplementedError

        def schedule(
                self,
                handler_ref: IoPipelineHandlerRef,
                delay_s: float,
                fn: ta.Callable[[], None],
        ) -> IoPipelineScheduling.Handle:
            self._pending.append((delay_s, fn))
            return self._Handle()

        def cancel_all(self, handler_ref: ta.Optional[IoPipelineHandlerRef] = None) -> None:
            raise NotImplementedError

        async def _task_body(self, delay: float, fn: ta.Callable[[], None]) -> None:
            await asyncio.sleep(delay)

            self._d._command_queue.put_nowait(PollAsyncioStreamIoPipelineDriver._ScheduledCommand(fn))  # noqa

        async def _flush_pending(self) -> None:
            if not (lst := self._pending):
                return

            for delay, fn in lst:
                task = asyncio.create_task(functools.partial(self._task_body, delay, fn)())
                self._tasks.add(task)
                task.add_done_callback(self._tasks.discard)

            self._pending = []

    @dc.dataclass(frozen=True)
    class _ScheduledCommand(_Command):
        fn: ta.Callable[[], None]

    async def _handle_command_scheduled(self, cmd: _ScheduledCommand) -> None:
        with self._pipeline.enter():
            cmd.fn()

    ##
    # shutdown

    class _ShutdownCommand(_Command):
        pass

    ##
    # command handling

    def _build_command_handlers(self) -> ta.Mapping[
        ta.Type[_Command],
        ta.Callable[[ta.Any], ta.Awaitable[None]],
    ]:
        return {
            PollAsyncioStreamIoPipelineDriver._FeedInCommand: self._handle_command_feed_in,
            PollAsyncioStreamIoPipelineDriver._ReadCompletedCommand: self._handle_command_read_completed,
            PollAsyncioStreamIoPipelineDriver._ScheduledCommand: self._handle_command_scheduled,
        }

    async def _handle_command(self, cmd: _Command) -> None:
        log.debug(lambda: f'Handling command: {cmd!r}')

        try:
            fn = self._command_handlers[cmd.__class__]
        except KeyError:
            raise TypeError(f'Unknown command type: {cmd.__class__}') from None

        await fn(cmd)

    ##
    # output handling

    async def _handle_output_final_output(self, msg: IoPipelineMessages.FinalOutput) -> ta.Optional[str]:
        self._shutdown_event.set()

        await self._close_writer()

        return 'stop'

    async def _handle_output_defer(self, msg: IoPipelineMessages.Defer) -> ta.Optional[str]:
        self._pipeline.run_deferred(msg)
        return None

    async def _handle_output_bytes(self, msg: ta.Any) -> None:
        for mv in ByteStreamBuffers.iter_segments(msg):
            if self._writer is not None and mv:
                self._writer.write(mv)

    async def _handle_output_flush_output(self, msg: IoPipelineFlowMessages.FlushOutput) -> ta.Optional[str]:
        if self._writer is not None:
            await self._writer.drain()
        return None

    async def _handle_output_ready_for_input(self, msg: IoPipelineFlowMessages.ReadyForInput) -> ta.Optional[str]:
        check.state(self._flow is not None)
        if self._config.strict_input_flow:
            check.state(not self._want_read)
        self._want_read = True
        self._want_read_event.set()
        return None

    async def _handle_output_await(self, msg: AsyncIoPipelineMessages.Await) -> ta.Optional[str]:
        try:
            result = await msg.obj

        except BaseException as e:  # noqa
            with self._pipeline.enter():
                msg.set_failed(e)

        else:
            with self._pipeline.enter():
                msg.set_succeeded(result)

        return None

    def _build_output_handlers(self) -> ta.Mapping[type, ta.Callable[[ta.Any], ta.Awaitable[ta.Optional[str]]]]:
        return {
            IoPipelineMessages.FinalOutput: self._handle_output_final_output,
            IoPipelineMessages.Defer: self._handle_output_defer,
            IoPipelineFlowMessages.FlushOutput: self._handle_output_flush_output,
            IoPipelineFlowMessages.ReadyForInput: self._handle_output_ready_for_input,
            AsyncIoPipelineMessages.Await: self._handle_output_await,
        }

    async def _handle_output(self, msg: ta.Any) -> str:
        log.debug(lambda: f'Handling output: {msg!r}')

        if ByteStreamBuffers.can_bytes(msg):
            await self._handle_output_bytes(msg)
            return 'handled'

        try:
            fn = self._output_handlers[msg.__class__]
        except KeyError:
            return 'unhandled'

        ret = await fn(msg)
        return ret if ret is not None else 'handled'

    ##
    # core loop

    def _has_pending_work(self) -> bool:
        if self._read_task is not None and not self._read_task.done():
            return True

        if hasattr(self, '_sched') and self._sched._tasks:  # noqa
            return True

        return False

    async def next(
            self,
            *,
            read: bool = True,
            raise_on_stall: bool = True,
    ) -> ta.Optional[ta.Any]:
        pipeline = await self._ensure_init()
        check.state(pipeline.is_ready)

        while True:
            if (out_msg := pipeline.output.poll()) is not None:
                handled = await self._handle_output(out_msg)

                if handled == 'handled':
                    continue

                elif handled == 'unhandled':
                    return out_msg

                elif handled == 'stop':
                    break

                else:
                    raise RuntimeError(f'Unknown handled value: {handled!r}')

            try:
                cmd = self._command_queue.get_nowait()
            except asyncio.QueueEmpty:
                if self._shutdown_event.is_set():
                    break

                if not read:
                    return None

                if raise_on_stall and not self._has_pending_work():
                    raise RuntimeError('Pipeline stalled') from None

                cmd = await self._command_queue.get()

            if isinstance(cmd, PollAsyncioStreamIoPipelineDriver._ShutdownCommand):
                break

            await self._handle_command(cmd)

            await self._sched._flush_pending()  # noqa

        pipeline.destroy()
        return None

    @async_exception_logging(alog)
    async def loop_until_done(self) -> None:
        try:
            while True:
                if (out := await self.next()) is not None:
                    raise TypeError(out)

                if not self._pipeline.is_ready:
                    break

        finally:
            await self.close()

    ##
    # lifecycle

    async def close(self) -> None:
        self._shutdown_event.set()

        self._want_read_event.set()

        await self._cancel_tasks(self._read_task, check_running=True)

        self._command_queue.put_nowait(PollAsyncioStreamIoPipelineDriver._ShutdownCommand())

        await self._close_writer()

        if hasattr(self, '_sched'):
            for t in list(self._sched._tasks):  # noqa
                if not t.done():
                    t.cancel()
            if self._sched._tasks:  # noqa
                await asyncio.gather(*self._sched._tasks, return_exceptions=True)  # noqa

        if self._has_init:
            try:
                if self._pipeline.is_ready:
                    self._pipeline.destroy()
            except AttributeError:
                pass

    async def __aenter__(self) -> 'PollAsyncioStreamIoPipelineDriver':  # noqa
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()
