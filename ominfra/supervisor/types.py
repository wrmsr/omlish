# ruff: noqa: UP006 UP007
import abc
import functools
import typing as ta

from omlish.io.fdio.handlers import FdioHandler

from .configs import ProcessConfig
from .configs import ProcessGroupConfig
from .events import ProcessOutputChannel
from .states import ProcessState
from .states import SupervisorState
from .utils.collections import KeyedCollectionAccessors
from .utils.ostypes import Pid
from .utils.ostypes import Rc


if ta.TYPE_CHECKING:
    from .dispatchers import Dispatchers


##


class ExitNow(Exception):  # noqa
    pass


ServerEpoch = ta.NewType('ServerEpoch', int)


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


class SupervisorStateManager(abc.ABC):
    @property
    @abc.abstractmethod
    def state(self) -> SupervisorState:
        raise NotImplementedError

    @abc.abstractmethod
    def set_state(self, state: SupervisorState) -> None:
        raise NotImplementedError


##


class HasDispatchers(abc.ABC):
    @abc.abstractmethod
    def get_dispatchers(self) -> 'Dispatchers':
        raise NotImplementedError


class ProcessDispatcher(FdioHandler, abc.ABC):
    @property
    @abc.abstractmethod
    def channel(self) -> ProcessOutputChannel:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def process(self) -> 'Process':
        raise NotImplementedError


class ProcessOutputDispatcher(ProcessDispatcher, abc.ABC):
    @abc.abstractmethod
    def remove_logs(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def reopen_logs(self) -> None:
        raise NotImplementedError


class ProcessInputDispatcher(ProcessDispatcher, abc.ABC):
    @abc.abstractmethod
    def write(self, chars: ta.Union[bytes, str]) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def flush(self) -> None:
        raise NotImplementedError


##


class Process(
    ConfigPriorityOrdered,
    HasDispatchers,
    abc.ABC,
):
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
    def pid(self) -> Pid:
        raise NotImplementedError

    #

    @abc.abstractmethod
    def finish(self, sts: Rc) -> None:
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

    @property
    @abc.abstractmethod
    def state(self) -> ProcessState:
        raise NotImplementedError

    @abc.abstractmethod
    def after_setuid(self) -> None:
        raise NotImplementedError


##


class ProcessGroup(
    ConfigPriorityOrdered,
    KeyedCollectionAccessors[str, Process],
    abc.ABC,
):
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
    def stop_all(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get_unstopped_processes(self) -> ta.List[Process]:
        raise NotImplementedError

    @abc.abstractmethod
    def before_remove(self) -> None:
        raise NotImplementedError
