from .base import Deploy
from .base import DeployConcern
from .nginx import NginxDeployConcern  # noqa
from .repo import RepoDeployConcern  # noqa
from .venv import VenvDeployConcern  # noqa


class DeployImpl(Deploy):
    concern_cls = DeployConcern

    def run(self) -> None:
        for c in self._concerns:
            c.run()
