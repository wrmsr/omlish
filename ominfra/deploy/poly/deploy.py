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
    ) -> None:
        super().__init__(config)
        self._site = site

    @property
    def site(self) -> Site:
        return self._site

    def run(self, runtime: Runtime) -> None:
        for c in self._concerns:
            c.run(runtime)
