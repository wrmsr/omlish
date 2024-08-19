# ruff: noqa: UP006 UP007
import os.path
import typing as ta

from omlish.lite.logs import log
from omlish.lite.subprocesses import subprocess_check_call

from .base import Concern
from .base import ConcernT
from .base import Deploy
from .base import DeployRuntime
from .repo import RepoConcern  # noqa
from .venv import VenvConcern  # noqa


class DeployRuntimeImpl(DeployRuntime):
    def __init__(self, deploy: 'Deploy') -> None:
        super().__init__()
        self._deploy = deploy

    def makedirs(self, p: str, exist_ok: bool = False) -> None:
        os.makedirs(p, exist_ok=exist_ok)

    def sh(self, *ss: str) -> None:
        s = ' && '.join(ss)
        log.info('Executing: %s', s)
        subprocess_check_call(s, shell=True)


##


CONCERN_CLS_BY_CONFIG_CLS: ta.Mapping[ta.Type[Concern.Config], ta.Type[Concern]] = {
    cls.Config: cls  # type: ignore
    for cls in Concern.__subclasses__()
}


class DeployImpl(Deploy):
    def __init__(
            self,
            config: Deploy.Config,
            runtime_cls: ta.Optional[ta.Type[DeployRuntime]] = None,
    ) -> None:
        super().__init__()
        self._config = config

        self._concerns = [
            CONCERN_CLS_BY_CONFIG_CLS[type(c)](c, self)
            for c in config.concerns
        ]
        self._concerns_by_cls: ta.Dict[ta.Type[Concern], Concern] = {}
        for c in self._concerns:
            if type(c) in self._concerns_by_cls:
                raise TypeError(f'Duplicate concern type: {c}')
            self._concerns_by_cls[type(c)] = c

        runtime: ta.Optional[DeployRuntime]
        if runtime_cls is not None:
            runtime = runtime_cls(self)  # type: ignore
        else:
            runtime = None
        self._runtime = runtime

    @property
    def config(self) -> 'Deploy.Config':
        return self._config

    @property
    def concerns(self) -> ta.List[Concern]:
        return self._concerns

    def concern(self, cls: ta.Type[ConcernT]) -> ConcernT:
        return self._concerns_by_cls[cls]  # type: ignore

    def runtime(self) -> DeployRuntime:
        if (runtime := self._runtime) is None:
            raise RuntimeError('No runtime present')
        return runtime

    def run(self) -> None:
        for c in self._concerns:
            c.run()
