from .base import Site
from .base import SiteConcern


class SiteImpl(Site):
    concern_cls = SiteConcern

    def run(self) -> None:
        pass

