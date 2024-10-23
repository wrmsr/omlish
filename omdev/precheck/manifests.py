import dataclasses as dc
import typing as ta

from ..manifests.load import ManifestLoader
from .base import Precheck
from .base import PrecheckContext


##


class ManifestsPrecheck(Precheck['ManifestsPrecheck.Config']):
    @dc.dataclass(frozen=True)
    class Config(Precheck.Config):
        pass

    def __init__(self, context: PrecheckContext, config: Config = Config()) -> None:
        super().__init__(context, config)

    async def run(self) -> ta.AsyncGenerator[Precheck.Violation, None]:
        for src_root in self._context.src_roots:
            ml = ManifestLoader()
            try:
                ml.load(src_root)
            except Exception as e:  # noqa
                yield Precheck.Violation(self, f'Error loading manifest for {src_root}: {e!r}')
