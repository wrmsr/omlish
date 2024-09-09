import abc
import dataclasses as dc
import itertools
import time
import typing as ta

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
class ProcessMailbox:
    main: aiu.StapledObjectStream


class ProcessBehavior(abc.ABC):
    async def process_init(self, proc: 'Process') -> None:
        pass

    @abc.abstractmethod
    async def process_run(self) -> None:
        raise NotImplementedError

    async def process_terminate(self, e: Exception | None) -> None:
        pass


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


class ProcessImpl(Process):
    def __init__(
            self,
            node: 'Node',
            pid: Pid,
            behavior: ProcessBehavior,
            mailbox: ProcessMailbox,
    ) -> None:
        super().__init__()
        self._node = node
        self._pid = pid
        self._behavior = behavior
        self._mailbox = mailbox

    @property
    def pid(self) -> Pid:
        return self._pid

    @property
    def behavior(self) -> ProcessBehavior:
        return self._behavior

    @property
    def mailbox(self) -> ProcessMailbox:
        return self._mailbox


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
        raise NotImplementedError


##


@dc.dataclass(frozen=True, kw_only=True)
class ProcessOptions:
    mailbox_size: int | None = None


class Node:
    def __init__(self) -> None:
        super().__init__()

        self._processes: dict[Pid, Process] = {}
        self._id_seq = itertools.count()

    async def spawn(
            self,
            behavior_fac: ta.Callable[[], ProcessBehavior],
            opts: ProcessOptions = ProcessOptions(),
    ) -> Process:
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

        return proc


#


class FooActor(Actor, ActorBehavior):
    async def handle_message(self, src: Pid, msg: ta.Any) -> None:
        raise TypeError()


async def _main() -> None:
    node = Node()
    proc = await node.spawn(FooActor)
    print(proc)


if __name__ == '__main__':
    anyio.run(_main)
