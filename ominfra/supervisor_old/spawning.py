# ruff: noqa: UP006 UP007
import abc
import dataclasses as dc

from .dispatchers import Dispatchers
from .pipes import ProcessPipes
from .types import Process
from .utils.ostypes import Pid


@dc.dataclass(frozen=True)
class SpawnedProcess:
    pid: Pid
    pipes: ProcessPipes
    dispatchers: Dispatchers


class ProcessSpawnError(RuntimeError):
    pass


class ProcessSpawning:
    @property
    @abc.abstractmethod
    def process(self) -> Process:
        raise NotImplementedError

    #

    @abc.abstractmethod
    def spawn(self) -> SpawnedProcess:  # Raises[ProcessSpawnError]
        raise NotImplementedError
