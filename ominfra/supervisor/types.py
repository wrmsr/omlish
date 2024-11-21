# ruff: noqa: UP006 UP007
import abc
import functools
import typing as ta

from .configs import ProcessConfig
from .configs import ProcessGroupConfig
from .configs import ServerConfig
from .states import ProcessState
from .states import SupervisorState


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
    def pid_history(self) -> ta.Dict[int, 'AbstractSubprocess']:
        raise NotImplementedError


@functools.total_ordering
class AbstractSubprocess(abc.ABC):
    @property
    @abc.abstractmethod
    def pid(self) -> int:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def config(self) -> ProcessConfig:
        raise NotImplementedError

    def __lt__(self, other):
        return self.config.priority < other.config.priority

    def __eq__(self, other):
        return self.config.priority == other.config.priority

    @property
    @abc.abstractmethod
    def context(self) -> ServerContext:
        raise NotImplementedError

    @abc.abstractmethod
    def finish(self, sts: int) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def remove_logs(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def reopen_logs(self) -> None:
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
    def create_auto_child_logs(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get_dispatchers(self) -> ta.Mapping[int, ta.Any]:  # dict[int, Dispatcher]
        raise NotImplementedError


@functools.total_ordering
class AbstractProcessGroup(abc.ABC):
    @property
    @abc.abstractmethod
    def config(self) -> ProcessGroupConfig:
        raise NotImplementedError

    def __lt__(self, other):
        return self.config.priority < other.config.priority

    def __eq__(self, other):
        return self.config.priority == other.config.priority
