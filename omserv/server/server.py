import errno
import logging
import math
import typing as ta

import anyio.abc

from omlish import check
from omlish import lang

from .config import Config
from .events import Closed
from .events import RawData
from .events import ServerEvent
from .events import Updated
from .protocols import ProtocolWrapper
from .sockets import parse_socket_addr
from .taskspawner import TaskSpawner
from .types import AppWrapper
from .workercontext import WorkerContext


log = logging.getLogger(__name__)


MAX_RECV = 2 ** 16


class ServerFactory(lang.Func3[AppWrapper, WorkerContext, anyio.abc.SocketStream, 'Server']):
    pass


class Server:
    def __init__(
            self,
            app: AppWrapper,
            context: WorkerContext,
            stream: anyio.abc.SocketStream,
            *,
            config: Config,
    ) -> None:
        super().__init__()

        self.app = app
        self.config = config
        self.context = context
        self.protocol: ProtocolWrapper
        self.send_lock = anyio.Lock()
        self.idle_lock = anyio.Lock()
        self.stream = stream

        self._idle_handle: anyio.abc.CancelScope | None = None
        self._task_spawner: TaskSpawner | None = None

    def __await__(self) -> ta.Generator[ta.Any, None, None]:
        return self.run().__await__()

    async def run(self) -> None:
        socket = self.stream._raw_socket  # noqa

        try:
            client = parse_socket_addr(socket.family, socket.getpeername())
            server = parse_socket_addr(socket.family, socket.getsockname())

            async with TaskSpawner() as task_spawner:
                self._task_spawner = task_spawner

                self.protocol = ProtocolWrapper(
                    self.app,
                    self.config,
                    self.context,
                    task_spawner,
                    client,
                    server,
                    self.protocol_send,
                )

                await self.protocol.initiate()
                await self._start_idle()
                await self._read_data()

        except* OSError:
            pass

        except* Exception as eg:
            for e in eg.exceptions:
                log.exception('Internal omlicorn error', exc_info=e)

        finally:
            await self._close()

    async def protocol_send(self, event: ServerEvent) -> None:
        if isinstance(event, RawData):
            async with self.send_lock:
                try:
                    with anyio.CancelScope() as cancel_scope:
                        cancel_scope.shield = True
                        await self.stream.send(event.data)

                except (anyio.BrokenResourceError, anyio.ClosedResourceError):
                    await self.protocol.handle(Closed())

        elif isinstance(event, Closed):
            await self._close()
            await self.protocol.handle(Closed())

        elif isinstance(event, Updated):
            if event.idle:
                await self._start_idle()
            else:
                await self._stop_idle()

    async def _read_data(self) -> None:
        while True:
            try:
                with anyio.fail_after(self.config.read_timeout or math.inf):
                    data = await self.stream.receive(MAX_RECV)

            except (
                    anyio.EndOfStream,
                    anyio.ClosedResourceError,
                    anyio.BrokenResourceError,
                    TimeoutError,
            ):
                break

            else:
                await self.protocol.handle(RawData(data))
                if data == b'':
                    break

        await self.protocol.handle(Closed())

    async def _close(self) -> None:
        try:
            await self.stream.send_eof()

        except OSError as e:
            if e.errno != errno.EBADF:
                raise

        except (
                anyio.BrokenResourceError,
                AttributeError,
                anyio.BusyResourceError,
                anyio.ClosedResourceError,
        ):
            # They're already gone, nothing to do - or it is a SSL stream
            pass

        await self.stream.aclose()

    async def _initiate_server_close(self) -> None:
        await self.protocol.handle(Closed())
        await self.stream.aclose()

    async def _start_idle(self) -> None:
        async with self.idle_lock:
            if self._idle_handle is None:
                self._idle_handle = await check.not_none(self._task_spawner).start(self._run_idle)

    async def _stop_idle(self) -> None:
        async with self.idle_lock:
            if self._idle_handle is not None:
                self._idle_handle.cancel()
            self._idle_handle = None

    async def _run_idle(
            self,
            task_status: anyio.abc.TaskStatus[ta.Any] = anyio.TASK_STATUS_IGNORED,
    ) -> None:
        cancel_scope = anyio.CancelScope()
        task_status.started(cancel_scope)
        with cancel_scope:
            with anyio.move_on_after(self.config.keep_alive_timeout):
                await self.context.terminated.wait()

            cancel_scope.shield = True
            await self._initiate_server_close()
