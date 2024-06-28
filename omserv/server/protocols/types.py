import abc

from ..events import ProtocolEvent
from ..events import ServerEvent


class Protocol(abc.ABC):
    @abc.abstractmethod
    async def initiate(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def handle(self, event: ServerEvent) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def stream_send(self, event: ProtocolEvent) -> None:
        raise NotImplementedError
