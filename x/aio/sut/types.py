import abc
import dataclasses as dc
import typing as ta

from omlish import lang


class Context(lang.Final):
    pass


class Service(lang.Abstract):
    @abc.abstractmethod
    async def serve(self, ctx: Context) -> None:
        raise NotImplementedError


SupervisorID = ta.NewType('SupervisorID', int)
ServiceID = ta.NewType('ServiceID', int)


@dc.dataclass(frozen=True)
class ServiceToken(lang.Final):
    supervisor: SupervisorID
    service: ServiceID


class Supervisor(lang.Abstract):
    @abc.abstractmethod
    async def add(self, service: Service) -> ServiceToken:
        raise NotImplementedError

    @abc.abstractmethod
    async def serve_background(self, ctx: Context) -> chan[error]:
        raise NotImplementedError

    @abc.abstractmethod
    async def serve(self, ctx: Context) -> error:
        raise NotImplementedError

    @abc.abstractmethod
    async def unstopped_service_report(self) -> tuple[UnstoppedServiceReport, error]:
        raise NotImplementedError

    @abc.abstractmethod
    async def remove(self, id: ServiceToken) -> error:
        raise NotImplementedError

    @abc.abstractmethod
    async def remove_and_wait(self, id: ServiceToken, timeout: float) -> error:
        raise NotImplementedError

    @abc.abstractmethod
    async def services(self) -> list[Service]:
        raise NotImplementedError
