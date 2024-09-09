import abc
import dataclasses as dc
import enum
import typing as ta

from omlish.asyncs import anyio as aiu


Atom = ta.NewType('Atom', str)


@dc.dataclass(frozen=True)
class Pid:
    id: int
    time: int


##


@dc.dataclass(frozen=True)
class MailboxMessage:
    src: Pid
    msg: ta.Any


##


@dc.dataclass(frozen=True)
class ProcessMailbox:
    main: aiu.MemoryStapledObjectStream


class ProcessBehavior(abc.ABC):
    async def process_init(self, proc: 'Process') -> None:
        pass

    @abc.abstractmethod
    async def process_run(self) -> None:
        raise NotImplementedError

    async def process_terminate(self, e: Exception | None) -> None:
        pass


class ProcessState(enum.Enum):
    INIT = enum.auto()
    SLEEP = enum.auto()
    RUN = enum.auto()
    WAIT_RESPONSE = enum.auto()
    TERMINATED = enum.auto()
    ZOMBIE = enum.auto()

    @property
    def alive(self) -> bool:
        return self in (ProcessState.INIT, ProcessState.SLEEP, ProcessState.RUN, ProcessState.WAIT_RESPONSE)


class Process(abc.ABC):
    @property
    @abc.abstractmethod
    def pid(self) -> Pid:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def behavior(self) -> ProcessBehavior:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def mailbox(self) -> ProcessMailbox:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def state(self) -> ProcessState:
        raise NotImplementedError


##


@dc.dataclass(frozen=True, kw_only=True)
class ProcessOptions:
    mailbox_size: int | None = None


class Node(abc.ABC):
    @abc.abstractmethod
    async def spawn(
            self,
            behavior_fac: ta.Callable[[], ProcessBehavior],
            opts: ProcessOptions = ProcessOptions(),
    ) -> Pid:
        raise NotImplementedError

    @abc.abstractmethod
    async def send(self, dst: Pid, msg: ta.Any) -> None:
        raise NotImplementedError
