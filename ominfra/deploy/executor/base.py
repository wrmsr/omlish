# ruff: noqa: UP006
import abc
import dataclasses as dc
import enum
import os.path
import shlex
import typing as ta

from omlish.lite.cached import cached_nullary
from omlish.lite.logs import log
from omlish.lite.subprocesses import subprocess_check_call

from ..configs import DeployConfig
from ..configs import HostConfig


##


class Phase(enum.Enum):
    HOST = enum.auto()
    ENV = enum.auto()
    BACKEND = enum.auto()
    FRONTEND = enum.auto()
    START_BACKEND = enum.auto()
    START_FRONTEND = enum.auto()


def run_in_phase(*ps: Phase):
    def inner(fn):
        fn.__deployment_phases__ = ps
        return fn
    return inner


class Concern(abc.ABC):
    def __init__(self, d: 'Deployment') -> None:
        super().__init__()
        self._d = d

    _phase_fns: ta.ClassVar[ta.Mapping[Phase, ta.Sequence[ta.Callable]]]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        dct: ta.Dict[Phase, ta.List[ta.Callable]] = {}
        for fn, ps in [
            (v, ps)
            for a in dir(cls)
            if not (a.startswith('__') and a.endswith('__'))
            for v in [getattr(cls, a, None)]
            for ps in [getattr(v, '__deployment_phases__', None)]
            if ps
        ]:
            dct.update({p: [*dct.get(p, []), fn] for p in ps})
        cls._phase_fns = dct

    @dc.dataclass(frozen=True)
    class Output(abc.ABC):
        path: str
        is_file: bool

    def outputs(self) -> ta.Sequence[Output]:
        return ()

    def run_phase(self, p: Phase) -> None:
        for fn in self._phase_fns.get(p, ()):
            fn.__get__(self, type(self))()


##


class Deployment:

    def __init__(
            self,
            cfg: DeployConfig,
            concern_cls_list: ta.List[ta.Type[Concern]],
            host_cfg: HostConfig = HostConfig(),
    ) -> None:
        super().__init__()
        self._cfg = cfg
        self._host_cfg = host_cfg

        self._concerns: ta.List[Concern] = [cls(self) for cls in concern_cls_list]

    @property
    def cfg(self) -> DeployConfig:
        return self._cfg

    @property
    def host_cfg(self) -> HostConfig:
        return self._host_cfg

    def sh(self, *ss: str) -> None:
        s = ' && '.join(ss)
        log.info('Executing: %s', s)
        subprocess_check_call(s, shell=True)

    def ush(self, *ss: str) -> None:
        s = ' && '.join(ss)
        self.sh(f'su - {self._host_cfg.username} -c {shlex.quote(s)}')

    @cached_nullary
    def home_dir(self) -> str:
        return os.path.expanduser(f'~{self._host_cfg.username}')

    @cached_nullary
    def deploy(self) -> None:
        for p in Phase:
            log.info('Phase %s', p.name)
            for c in self._concerns:
                c.run_phase(p)

        log.info('Shitty deploy complete!')
