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


##


@dc.dataclass(frozen=True)
class UnstoppedService(lang.Final):
    supervisor_path: list['Supervisor']
    service: Service
    name: str
    service_token: ServiceToken


type UnstoppedServiceReport = list[UnstoppedService]


class Supervisor(lang.Abstract):
    @abc.abstractmethod
    async def add(self, service: Service) -> ServiceToken:
        raise NotImplementedError

    @abc.abstractmethod
    async def serve_background(self, ctx: Context) -> anyio.abc.ObjectReceiveStream[Exception]:
        raise NotImplementedError

    @abc.abstractmethod
    async def serve(self, ctx: Context) -> Exception:
        raise NotImplementedError

    @abc.abstractmethod
    async def unstopped_service_report(self) -> tuple[UnstoppedServiceReport, Exception]:
        raise NotImplementedError

    @abc.abstractmethod
    async def remove(self, id: ServiceToken) -> Exception:
        raise NotImplementedError

    @abc.abstractmethod
    async def remove_and_wait(self, id: ServiceToken, timeout: Duration) -> Exception:
        raise NotImplementedError

    @abc.abstractmethod
    async def services(self) -> list[Service]:
        raise NotImplementedError
