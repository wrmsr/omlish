import abc
import typing as ta

import anyio.abc
import anyio.streams.stapled

from omlish import check

from .types import MailboxMessage
from .types import Pid
from .types import Process
from .types import ProcessBehavior


class ActorBehavior(ProcessBehavior, abc.ABC):
    async def init(self) -> None:
        pass

    @abc.abstractmethod
    async def handle_message(self, src: Pid, msg: ta.Any) -> None:
        raise NotImplementedError


class Actor(ProcessBehavior):
    def __init__(self) -> None:
        super().__init__()

        self._proc: Process | None = None
        self._behavior: ActorBehavior | None = None

    async def process_init(self, proc: 'Process') -> None:
        await super().process_init(proc)

        check.none(self._proc)
        check.none(self._behavior)

        behavior = check.isinstance(proc.behavior, ActorBehavior)

        self._proc = proc
        self._behavior = behavior

        await behavior.init()

    async def process_run(self) -> None:
        while True:
            try:
                msg = self._proc.mailbox.main.receive_stream.receive_nowait()
            except anyio.WouldBlock:
                return

            mbm = check.isinstance(msg, MailboxMessage)
            await self._behavior.handle_message(mbm.src, mbm.msg)
