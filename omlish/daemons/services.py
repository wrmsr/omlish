import abc
import typing as ta

from .. import cached
from .. import check
from .. import dataclasses as dc
from .. import lang
from ..configs.classes import Configurable
from .daemon import Daemon
from .targets import Target
from .targets import TargetRunner
from .targets import target_runner_for


ServiceConfigT = ta.TypeVar('ServiceConfigT', bound='Service.Config')


##


class Service(Configurable[ServiceConfigT], lang.Abstract):
    class Config(Configurable.Config, lang.Abstract):
        pass

    @classmethod
    def from_config(cls, config: Config) -> 'Service':
        return check.isinstance(config.configurable_cls(config), cls)

    #

    @abc.abstractmethod
    def _run(self) -> None:
        raise NotImplementedError

    def run(self) -> None:
        self._run()

    @classmethod
    def run_config(cls, config: Config) -> None:
        return cls.from_config(config).run()


##


class ServiceTarget(Target):
    svc: Service


class ServiceTargetRunner(TargetRunner, dc.Frozen):
    target: ServiceTarget

    def run(self) -> None:
        self.target.svc.run()


@target_runner_for.register
def _(target: ServiceTarget) -> ServiceTargetRunner:
    return ServiceTargetRunner(target)


#


class ServiceConfigTarget(Target):
    cfg: Service.Config


class ServiceConfigTargetRunner(TargetRunner, dc.Frozen):
    target: ServiceConfigTarget

    def run(self) -> None:
        Service.run_config(self.target.cfg)


@target_runner_for.register
def _(target: ServiceConfigTarget) -> ServiceConfigTargetRunner:
    return ServiceConfigTargetRunner(target)


##


@dc.dataclass(frozen=True)
class ServiceDaemon(lang.Final):
    service: Service | Service.Config

    @cached.function
    def service_(self) -> Service:
        if isinstance(self.service, Service):
            return self.service
        elif isinstance(self.service, Service.Config):
            return Service.from_config(self.service)
        else:
            raise TypeError(self.service)

    #

    daemon: Daemon | Daemon.Config = Daemon.Config()

    @cached.function
    def daemon_(self) -> Daemon:
        if isinstance(self.daemon, Daemon):
            return self.daemon
        elif isinstance(self.daemon, Daemon.Config):
            return Daemon(Target.of(self.service_()), self.daemon)
        else:
            raise TypeError(self.daemon)
