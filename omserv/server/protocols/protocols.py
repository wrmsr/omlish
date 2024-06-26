import typing as ta

from ..config import Config
from ..events import RawData
from ..events import ServerEvent
from ..taskspawner import TaskSpawner
from ..types import AppWrapper
from ..workercontext import WorkerContext
from .h11 import H11Protocol
from .h11 import H2CProtocolRequiredError
from .h11 import H2ProtocolAssumedError
from .h2 import H2Protocol
from .types import Protocol


class ProtocolWrapper:
    def __init__(
            self,
            app: AppWrapper,
            config: Config,
            context: WorkerContext,
            task_spawner: TaskSpawner,
            client: ta.Optional[tuple[str, int]],
            server: ta.Optional[tuple[str, int]],
            send: ta.Callable[[ServerEvent], ta.Awaitable[None]],
            alpn_protocol: ta.Optional[str] = None,
    ) -> None:
        super().__init__()
        self.app = app
        self.config = config
        self.context = context
        self.task_spawner = task_spawner
        self.client = client
        self.server = server
        self.send = send
        self.protocol: Protocol
        if alpn_protocol == 'h2':
            self.protocol = H2Protocol(
                self.app,
                self.config,
                self.context,
                self.task_spawner,
                self.client,
                self.server,
                self.send,
            )
        else:
            self.protocol = H11Protocol(
                self.app,
                self.config,
                self.context,
                self.task_spawner,
                self.client,
                self.server,
                self.send,
            )

    async def initiate(self) -> None:
        return await self.protocol.initiate()

    async def handle(self, event: ServerEvent) -> None:
        try:
            return await self.protocol.handle(event)

        except H2ProtocolAssumedError as error:
            self.protocol = H2Protocol(
                self.app,
                self.config,
                self.context,
                self.task_spawner,
                self.client,
                self.server,
                self.send,
            )
            await self.protocol.initiate()
            if error.data != b'':
                return await self.protocol.handle(RawData(data=error.data))

        except H2CProtocolRequiredError as error:
            self.protocol = H2Protocol(
                self.app,
                self.config,
                self.context,
                self.task_spawner,
                self.client,
                self.server,
                self.send,
            )
            await self.protocol.initiate(error.headers, error.settings)
            if error.data != b'':
                return await self.protocol.handle(RawData(data=error.data))
