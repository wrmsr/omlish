import abc
import dataclasses as dc

from .dispatchers import Dispatchers
from .pipes import ProcessPipes
from .types import Process


@dc.dataclass(frozen=True)
class SpawnedProcess:
    pid: int
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
