import abc
import dataclasses as dc
import enum
import itertools
import time
import typing as ta

import anyio.abc
import anyio.streams.stapled

from omlish.asyncs import anyio as aiu
from omlish import check


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


class ProcessImpl(Process):
    def __init__(
            self,
            node: 'NodeImpl',
            pid: Pid,
            behavior: ProcessBehavior,
            mailbox: ProcessMailbox,
    ) -> None:
        super().__init__()
        self._node = node
        self._pid = pid
        self._behavior = behavior
        self._mailbox = mailbox

        self._state = ProcessState.INIT

    @property
    def pid(self) -> Pid:
        return self._pid

    @property
    def behavior(self) -> ProcessBehavior:
        return self._behavior

    @property
    def mailbox(self) -> ProcessMailbox:
        return self._mailbox

    @property
    def state(self) -> ProcessState:
        return self._state

    async def _run(self) -> None:
        if self._state != ProcessState.SLEEP:
            return
        self._state = ProcessState.RUN

        async def _inner():
            while True:
                await self._behavior.process_run()

                if self._state != ProcessState.RUN:
                    raise Exception('Killed')
                self._state = ProcessState.SLEEP

                if not self._mailbox.main.receive_stream.statistics().current_buffer_used:
                    break

                if self._state != ProcessState.SLEEP:
                    break
                self._state = ProcessState.RUN


        self._node._tg.start_soon(_inner)  # noqa


##


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

            print(msg)
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
    def send(self, dst: Pid, msg: ta.Any) -> None:
        raise NotImplementedError


class NodeImpl(Node):
    def __init__(
            self,
            tg: anyio.abc.TaskGroup,
    ) -> None:
        super().__init__()

        self._tg = tg

        self._processes: dict[Pid, ProcessImpl] = {}
        self._id_seq = itertools.count()

    async def spawn(
            self,
            behavior_fac: ta.Callable[[], ProcessBehavior],
            opts: ProcessOptions = ProcessOptions(),
    ) -> Pid:
        pid = Pid(
            next(self._id_seq),
            int(time.monotonic()),
        )

        behavior = behavior_fac()

        mailbox = ProcessMailbox(
            aiu.create_stapled_memory_object_stream(opts.mailbox_size or 0),
        )

        proc = ProcessImpl(
            self,
            pid,
            behavior,
            mailbox,
        )

        await behavior.process_init(proc)

        proc._state = ProcessState.SLEEP  # noqa
        self._processes[pid] = proc

        await proc._run()  # noqa

        return proc.pid

    def send(self, dst: Pid, msg: ta.Any) -> None:
        raise NotImplementedError


#


class FooActor(Actor, ActorBehavior):
    async def handle_message(self, src: Pid, msg: ta.Any) -> None:
        raise TypeError()


async def _main() -> None:
    async with anyio.create_task_group() as tg:
        node = NodeImpl(tg)
        pid = await node.spawn(FooActor)
        print(pid)


if __name__ == '__main__':
    anyio.run(_main)
