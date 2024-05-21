import asyncio
import typing as ta

from .config import Config
from .events import Closed
from .events import RawData
from .events import ServerEvent
from .events import Updated
from .protocols import ProtocolWrapper
from .sockets import parse_socket_addr
from .taskgroups import TaskGroup
from .types import AppWrapper
from .workercontext import WorkerContext


MAX_RECV = 2 ** 16


class TCPServer:
    def __init__(
            self,
            app: AppWrapper,
            loop: asyncio.AbstractEventLoop,
            config: Config,
            context: WorkerContext,
            reader: asyncio.StreamReader,
            writer: asyncio.StreamWriter,
    ) -> None:
        super().__init__()
        self.app = app
        self.config = config
        self.context = context
        self.loop = loop
        self.protocol: ProtocolWrapper
        self.reader = reader
        self.writer = writer
        self.send_lock = asyncio.Lock()
        self.idle_lock = asyncio.Lock()

        self._idle_handle: ta.Optional[asyncio.Task] = None

    def __await__(self) -> ta.Generator[ta.Any, None, None]:
        return self.run().__await__()

    async def run(self) -> None:
        socket = self.writer.get_extra_info("socket")
        try:
            client = parse_socket_addr(socket.family, socket.getpeername())
            server = parse_socket_addr(socket.family, socket.getsockname())

            async with TaskGroup(self.loop) as task_group:
                self.protocol = ProtocolWrapper(
                    self.app,
                    self.config,
                    self.context,
                    task_group,
                    client,
                    server,
                    self.protocol_send,
                )
                await self.protocol.initiate()
                await self._start_idle()
                await self._read_data()
        except OSError:
            pass
        finally:
            await self._close()

    async def protocol_send(self, event: ServerEvent) -> None:
        if isinstance(event, RawData):
            async with self.send_lock:
                try:
                    self.writer.write(event.data)
                    await self.writer.drain()
                except (ConnectionError, RuntimeError):
                    await self.protocol.handle(Closed())
        elif isinstance(event, Closed):
            await self._close()
        elif isinstance(event, Updated):
            if event.idle:
                await self._start_idle()
            else:
                await self._stop_idle()

    async def _read_data(self) -> None:
        while not self.reader.at_eof():
            try:
                data = await asyncio.wait_for(self.reader.read(MAX_RECV), self.config.read_timeout)
            except (
                    ConnectionError,
                    OSError,
                    asyncio.TimeoutError,
                    TimeoutError,
            ):
                break
            else:
                await self.protocol.handle(RawData(data))

        await self.protocol.handle(Closed())

    async def _close(self) -> None:
        try:
            self.writer.write_eof()
        except (NotImplementedError, OSError, RuntimeError):
            pass  # Likely SSL connection

        try:
            self.writer.close()
            await self.writer.wait_closed()
        except (
                BrokenPipeError,
                ConnectionAbortedError,
                ConnectionResetError,
                RuntimeError,
                asyncio.CancelledError,
        ):
            pass  # Already closed
        finally:
            await self._stop_idle()

    async def _initiate_server_close(self) -> None:
        await self.protocol.handle(Closed())
        self.writer.close()

    async def _start_idle(self) -> None:
        async with self.idle_lock:
            if self._idle_handle is None:
                self._idle_handle = self.loop.create_task(self._run_idle())

    async def _stop_idle(self) -> None:
        async with self.idle_lock:
            if self._idle_handle is not None:
                self._idle_handle.cancel()
                try:
                    await self._idle_handle
                except asyncio.CancelledError:
                    pass
            self._idle_handle = None

    async def _run_idle(self) -> None:
        try:
            await asyncio.wait_for(self.context.terminated.wait(), self.config.keep_alive_timeout)
        except asyncio.TimeoutError:
            pass
        await asyncio.shield(self._initiate_server_close())
