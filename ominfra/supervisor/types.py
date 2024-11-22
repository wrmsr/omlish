# ruff: noqa: UP006 UP007
import abc
import functools
import typing as ta

from .configs import ProcessConfig
from .configs import ProcessGroupConfig
from .configs import ServerConfig
from .states import ProcessState
from .states import SupervisorState


if ta.TYPE_CHECKING:
    from .dispatchers import Dispatchers


##


@functools.total_ordering
class ConfigPriorityOrdered(abc.ABC):
    @property
    @abc.abstractmethod
    def config(self) -> ta.Any:
        raise NotImplementedError

    def __lt__(self, other):
        return self.config.priority < other.config.priority

    def __eq__(self, other):
        return self.config.priority == other.config.priority


##


class ServerContext(abc.ABC):
    @property
    @abc.abstractmethod
    def config(self) -> ServerConfig:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def state(self) -> SupervisorState:
        raise NotImplementedError

    @abc.abstractmethod
    def set_state(self, state: SupervisorState) -> None:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def pid_history(self) -> ta.Dict[int, 'Process']:
        raise NotImplementedError


##


class Dispatcher(abc.ABC):
    @property
    @abc.abstractmethod
    def process(self) -> 'Process':
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def channel(self) -> str:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def fd(self) -> int:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def closed(self) -> bool:
        raise NotImplementedError

    #

    @abc.abstractmethod
    def close(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def handle_error(self) -> None:
        raise NotImplementedError

    #

    @abc.abstractmethod
    def readable(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def writable(self) -> bool:
        raise NotImplementedError

    #

    def handle_read_event(self) -> None:
        raise TypeError

    def handle_write_event(self) -> None:
        raise TypeError


class OutputDispatcher(Dispatcher, abc.ABC):
    @abc.abstractmethod
    def remove_logs(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def reopen_logs(self) -> None:
        raise NotImplementedError


class InputDispatcher(Dispatcher, abc.ABC):
    @abc.abstractmethod
    def write(self, chars: ta.Union[bytes, str]) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def flush(self) -> None:
        raise NotImplementedError


##


class Process(ConfigPriorityOrdered, abc.ABC):
    @property
    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def config(self) -> ProcessConfig:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def group(self) -> 'ProcessGroup':
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def pid(self) -> int:
        raise NotImplementedError

    #

    @property
    @abc.abstractmethod
    def context(self) -> ServerContext:
        raise NotImplementedError

    @abc.abstractmethod
    def finish(self, sts: int) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def stop(self) -> ta.Optional[str]:
        raise NotImplementedError

    @abc.abstractmethod
    def give_up(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def transition(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get_state(self) -> ProcessState:
        raise NotImplementedError

    @abc.abstractmethod
    def after_setuid(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get_dispatchers(self) -> 'Dispatchers':
        raise NotImplementedError


##


class ProcessGroup(ConfigPriorityOrdered, abc.ABC):
    @property
    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def config(self) -> ProcessGroupConfig:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def by_name(self) -> ta.Mapping[str, Process]:
        raise NotImplementedError

    #

    @abc.abstractmethod
    def __iter__(self) -> ta.Iterator[Process]:
        raise NotImplementedError

    @abc.abstractmethod
    def __len__(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def __contains__(self, name: str) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def __getitem__(self, name: str) -> Process:
        raise NotImplementedError

    #

    @abc.abstractmethod
    def stop_all(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get_unstopped_processes(self) -> ta.List[Process]:
        raise NotImplementedError

    @abc.abstractmethod
    def before_remove(self) -> None:
        raise NotImplementedError
