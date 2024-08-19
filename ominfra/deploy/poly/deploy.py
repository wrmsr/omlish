# @omdev-amalg ./_deploy.py
# ruff: noqa: UP006 UP007
import typing as ta

from .base import Deploy
from .base import DeployConcern
from .base import DeployConcernT
from .base import Runtime
from .nginx import NginxDeployConcern  # noqa
from .repo import RepoDeployConcern  # noqa
from .venv import VenvDeployConcern  # noqa


DEPLOY_CONCERN_CLS_BY_CONFIG_CLS: ta.Mapping[ta.Type[DeployConcern.Config], ta.Type[DeployConcern]] = {
    cls.Config: cls  # type: ignore
    for cls in DeployConcern.__subclasses__()
}


class DeployImpl(Deploy):
    def __init__(
            self,
            config: Deploy.Config,
            runtime: ta.Optional[Runtime] = None,
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

        self._runtime = runtime

    @property
    def config(self) -> 'Deploy.Config':
        return self._config

    @property
    def concerns(self) -> ta.List[DeployConcern]:
        return self._concerns

    def concern(self, cls: ta.Type[DeployConcernT]) -> DeployConcernT:
        return self._concerns_by_cls[cls]  # type: ignore

    def runtime(self) -> Runtime:
        if (runtime := self._runtime) is None:
            raise RuntimeError('No runtime present')
        return runtime

    def run(self) -> None:
        for c in self._concerns:
            c.run()
