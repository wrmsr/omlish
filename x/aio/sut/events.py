import abc
import dataclasses as dc
import enum
import typing as ta

from omlish import lang


type EventHook = ta.Callable[['Event'], None]


class EventType(enum.Enum):
    StopTimeout = enum.auto()
    ServicePanic = enum.auto()
    ServiceTerminate = enum.auto()
    Backoff = enum.auto()
    Resume = enum.auto()


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
        return EventType.StopTimeout


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
        return EventType.ServicePanic


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
        return EventType.ServiceTerminate


class EventBackoff(Event):
    Supervisor: Supervisor
    Supervisor_name: str

    @property
    def type(self) -> EventType:
        return EventType.Backoff


class EventResume(Event):
    Supervisor: Supervisor
    Supervisor_name: str

    @property
    def type(self) -> EventType:
        return EventType.Resume
