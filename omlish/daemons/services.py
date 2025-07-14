"""
TODO:
 - jsonl pidfile
  - time started
  - code version / revision
  - venv?
"""
import abc
import threading
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


ServiceT = ta.TypeVar('ServiceT', bound='Service')
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
class ServiceDaemon(lang.Final, ta.Generic[ServiceT, ServiceConfigT]):
    service: ServiceT | ServiceConfigT

    @cached.function
    def service_config(self) -> ServiceConfigT:
        with self._lock:
            if isinstance(self.service, Service):
                return self.service.config
            elif isinstance(self.service, Service.Config):
                return self.service
            else:
                raise TypeError(self.service)

    @cached.function
    def service_(self) -> ServiceT:
        with self._lock:
            if isinstance(self.service, Service):
                return self.service
            elif isinstance(self.service, Service.Config):
                return Service.from_config(self.service)  # type: ignore[return-value]
            else:
                raise TypeError(self.service)

    #

    daemon: Daemon | Daemon.Config = Daemon.Config()

    @cached.function
    def daemon_config(self) -> Daemon.Config:
        with self._lock:
            if isinstance(self.daemon, Daemon):
                return self.daemon.config
            elif isinstance(self.daemon, Daemon.Config):
                return self.daemon
            else:
                raise TypeError(self.daemon)

    @cached.function
    def daemon_(self) -> Daemon:
        with self._lock:
            if isinstance(self.daemon, Daemon):
                return self.daemon
            elif isinstance(self.daemon, Daemon.Config):
                return Daemon(Target.of(self.service_()), self.daemon)
            else:
                raise TypeError(self.daemon)

    #

    _lock: threading.RLock = dc.field(default_factory=lambda: threading.RLock(), init=False)
