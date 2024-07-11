import abc
import dataclasses as dc
import enum
import typing as ta

from omlish import lang

from .types import Service
from .types import Supervisor


type EventHook = ta.Callable[['Event'], None]


class EventType(enum.Enum):
    STOP_TIMEOUT = enum.auto()
    SERVICE_PANIC = enum.auto()
    SERVICE_TERMINATE = enum.auto()
    BACKOFF = enum.auto()
    RESUME = enum.auto()


class Event(lang.Abstract):
    @property
    @abc.abstractmethod
    def type(self) -> EventType:
        raise NotImplementedError


@dc.dataclass()
class EventStopTimeout(Event):
    supervisor: Supervisor
    supervisor_name: str
    service: Service
    service_name: str

    @property
    def type(self) -> EventType:
        return EventType.STOP_TIMEOUT


@dc.dataclass()
class EventServicePanic(Event):
    supervisor: Supervisor
    supervisor_name: str
    service: Service
    service_name: str
    current_failures: float
    failure_threshold: float
    restarting: bool
    panic_msg: str
    stacktrace: str

    @property
    def type(self) -> EventType:
        return EventType.SERVICE_PANIC


class EventServiceTerminate(Event):
    supervisor: Supervisor
    supervisor_name: str
    service: Service
    service_name: str
    current_failures: float
    failure_threshold: float
    restarting: bool
    err: ta.Any

    @property
    def type(self) -> EventType:
        return EventType.SERVICE_TERMINATE


class EventBackoff(Event):
    Supervisor: Supervisor
    Supervisor_name: str

    @property
    def type(self) -> EventType:
        return EventType.BACKOFF


class EventResume(Event):
    Supervisor: Supervisor
    Supervisor_name: str

    @property
    def type(self) -> EventType:
        return EventType.RESUME
