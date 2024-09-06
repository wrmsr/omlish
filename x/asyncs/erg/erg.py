import abc
import dataclasses as dc
import typing as ta

import anyio.streams.stapled

from omlish.asyncs import anyio as aiu


Atom = ta.NewType('Atom', str)


@dc.dataclass(frozen=True)
class Pid:
    id: int
    creation: int


##


@dc.dataclass(frozen=True)
class ProcessMailbox:
    main: aiu.StapledObjectStream = dc.field(default_factory=lambda: aiu.create_stapled_memory_object_stream())


class ProcessBehavior(abc.ABC):
    async def init(self) -> None:
        pass

    @abc.abstractmethod
    async def run(self) -> None:
        raise NotImplementedError

    async def terminate(self, e: Exception | None) -> None:
        pass


class Process(abc.ABC):
    @property
    @abc.abstractmethod
    def pid(self) -> Pid:
        raise NotImplementedError


##


class Actor:
    pass


##


class Node:
    def __init__(self) -> None:
        super().__init__()
        self._processes: dict[Pid, Process] = {}


#


async def _main() -> None:
    pass


if __name__ == '__main__':
    anyio.run(_main)
