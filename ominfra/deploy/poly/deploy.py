# ruff: noqa: UP007
import typing as ta

from .base import Deploy
from .base import DeployConcern
from .base import Runtime
from .base import Site


class DeployImpl(Deploy):
    concern_cls = DeployConcern

    def __init__(
            self,
            config: Deploy.Config,
            site: Site,
            *,
            runtime: ta.Optional[Runtime] = None,
    ) -> None:
        super().__init__(config, runtime=runtime)
        self._site = site

    @property
    def site(self) -> Site:
        return self._site

    def run(self) -> None:
        for c in self._concerns:
            c.run()
