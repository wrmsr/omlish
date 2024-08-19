# ruff: noqa: UP006 UP007
import typing as ta

from .base import Site
from .base import SiteConcern
from .base import SiteConcernT
from .base import Runtime


SITE_CONCERN_CLS_BY_CONFIG_CLS: ta.Mapping[ta.Type[SiteConcern.Config], ta.Type[SiteConcern]] = {}


class SiteImpl(Site):
    def __init__(
            self,
            config: Site.Config,
            runtime: ta.Optional[Runtime] = None,
    ) -> None:
        super().__init__()
        self._config = config

        self._concerns = [
            SITE_CONCERN_CLS_BY_CONFIG_CLS[type(c)](c, self)
            for c in config.concerns
        ]
        self._concerns_by_cls: ta.Dict[ta.Type[SiteConcern], SiteConcern] = {}
        for c in self._concerns:
            if type(c) in self._concerns_by_cls:
                raise TypeError(f'Duplicate concern type: {c}')
            self._concerns_by_cls[type(c)] = c

        self._runtime = runtime

    @property
    def config(self) -> 'Site.Config':
        return self._config

    @property
    def concerns(self) -> ta.List[SiteConcern]:
        return self._concerns

    def concern(self, cls: ta.Type[SiteConcernT]) -> SiteConcernT:
        return self._concerns_by_cls[cls]  # type: ignore

    def runtime(self) -> Runtime:
        if (runtime := self._runtime) is None:
            raise RuntimeError('No runtime present')
        return runtime

    def run(self) -> None:
        for c in self._concerns:
            c.run()
