# @omdev-amalg ./_deploy.py
# ruff: noqa: UP006 UP007
import os.path
import typing as ta

from omlish.lite.logs import log
from omlish.lite.subprocesses import subprocess_check_call

from .base import Deploy
from .base import DeployConcern
from .base import DeployConcernT
from .base import DeployRuntime
from .nginx import NginxDeployConcern  # noqa
from .repo import RepoDeployConcern  # noqa
from .venv import VenvDeployConcern  # noqa


class DeployRuntimeImpl(DeployRuntime):
    def __init__(self, deploy: 'Deploy') -> None:
        super().__init__()
        self._deploy = deploy

    def make_dirs(self, p: str, exist_ok: bool = False) -> None:
        os.makedirs(p, exist_ok=exist_ok)

    def write_file(self, p: str, c: ta.Union[str, bytes]) -> None:
        if os.path.exists(p):
            raise RuntimeError(f'Path exists: {p}')
        with open(p, 'w' if isinstance(c, str) else 'wb') as f:
            f.write(c)

    def sh(self, *ss: str) -> None:
        s = ' && '.join(ss)
        log.info('Executing: %s', s)
        subprocess_check_call(s, shell=True)


##


DEPLOY_CONCERN_CLS_BY_CONFIG_CLS: ta.Mapping[ta.Type[DeployConcern.Config], ta.Type[DeployConcern]] = {
    cls.Config: cls  # type: ignore
    for cls in DeployConcern.__subclasses__()
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
            DEPLOY_CONCERN_CLS_BY_CONFIG_CLS[type(c)](c, self)
            for c in config.concerns
        ]
        self._concerns_by_cls: ta.Dict[ta.Type[DeployConcern], DeployConcern] = {}
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
    def concerns(self) -> ta.List[DeployConcern]:
        return self._concerns

    def concern(self, cls: ta.Type[DeployConcernT]) -> DeployConcernT:
        return self._concerns_by_cls[cls]  # type: ignore

    def runtime(self) -> DeployRuntime:
        if (runtime := self._runtime) is None:
            raise RuntimeError('No runtime present')
        return runtime

    def run(self) -> None:
        for c in self._concerns:
            c.run()
