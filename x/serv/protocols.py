import typing as ta

from .config import Config
from .events import ServerEvent
from .h11_ import H11Protocol
from .h11_ import H2ProtocolAssumedError
from .taskgroups import TaskGroup
from .types import AppWrapper
from .workercontext import WorkerContext


class ProtocolWrapper:
    def __init__(
            self,
            app: AppWrapper,
            config: Config,
            context: WorkerContext,
            task_group: TaskGroup,
            client: ta.Optional[tuple[str, int]],
            server: ta.Optional[tuple[str, int]],
            send: ta.Callable[[ServerEvent], ta.Awaitable[None]],
    ) -> None:
        super().__init__()
        self.app = app
        self.config = config
        self.context = context
        self.task_group = task_group
        self.client = client
        self.server = server
        self.send = send
        self.protocol = H11Protocol(
            self.app,
            self.config,
            self.context,
            self.task_group,
            self.client,
            self.server,
            self.send,
        )

    async def initiate(self) -> None:
        return await self.protocol.initiate()

    async def handle(self, event: ServerEvent) -> None:
        try:
            return await self.protocol.handle(event)
        except H2ProtocolAssumedError as error:  # noqa
            raise
