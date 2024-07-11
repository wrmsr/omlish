import abc
import dataclasses as dc
import typing as ta

import anyio.abc

from omlish import lang


##


type Time = float
type Duration = float


##


type CancelFunc = ta.Callable[[], None]


class Context(lang.Abstract):
    @abc.abstractmethod
    async def done(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def err(self) -> Exception | None:
        raise NotImplementedError


##


class DoNotRestart(Exception):
    """Can be returned by a service to voluntarily not be restarted."""

    def __init__(self) -> None:
        super().__init__("service should not be restarted")


class TerminateSupervisorTree(Exception):
    """Can can be returned by a service to terminate the entire supervision tree above it as well."""
    def __init__(self) -> None:
        super().__init__("tree should be terminated")


##


class Service(lang.Abstract):
    @abc.abstractmethod
    async def serve(self, ctx: Context) -> Exception | None:
        raise NotImplementedError


SupervisorId = ta.NewType('SupervisorId', int)
ServiceId = ta.NewType('ServiceId', int)


@dc.dataclass(frozen=True)
class ServiceToken(lang.Final):
    supervisor: SupervisorId
    service: ServiceId

    ZERO: ta.ClassVar['ServiceToken']


ServiceToken.ZERO = ServiceToken(SupervisorId(0), ServiceId(0))


##


@dc.dataclass(frozen=True)
class UnstoppedService(lang.Final):
    supervisor_path: list['Supervisor']
    service: Service
    name: str
    service_token: ServiceToken


type UnstoppedServiceReport = list[UnstoppedService]


class HasSupervisor(lang.Abstract):
    @abc.abstractmethod
    def supervisor(self) -> ta.Optional['Supervisor']:
        raise NotImplementedError


class Supervisor(HasSupervisor):
    @abc.abstractmethod
    async def add(self, service: Service) -> ServiceToken:
        raise NotImplementedError

    @abc.abstractmethod
    async def serve_background(self, ctx: Context) -> anyio.abc.ObjectReceiveStream[Exception]:
        raise NotImplementedError

    @abc.abstractmethod
    async def serve(self, ctx: Context) -> Exception | None:
        raise NotImplementedError

    @abc.abstractmethod
    async def unstopped_service_report(self) -> tuple[UnstoppedServiceReport, Exception | None]:
        raise NotImplementedError

    @abc.abstractmethod
    async def remove(self, sid: ServiceToken) -> Exception | None:
        raise NotImplementedError

    @abc.abstractmethod
    async def remove_and_wait(self, sid: ServiceToken, timeout: Duration) -> Exception | None:
        raise NotImplementedError

    @abc.abstractmethod
    async def services(self) -> list[Service]:
        raise NotImplementedError
