# -*- coding: utf-8 -*-


from typing import Any, List
from typing_extensions import Protocol


class Server(Protocol):
    """Asyncio event loop does not publish an interface for server objects."""

    def close(self) -> None:
        ...  # pragma: no cover

    async def wait_closed(self) -> None:
        ...  # pragma: no cover


class SocketServer(Server):
    """Asyncio event loop does not publish an interface for server objects."""

    @property
    def sockets(self) -> List[Any]:
        ...  # pragma: no cover
