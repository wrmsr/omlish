from .base import Runtime
from .base import Site
from .base import SiteConcern


class SiteImpl(Site):
    concern_cls = SiteConcern

    def run(self, runtime: Runtime) -> None:
        for c in self._concerns:
            c.run(runtime)
