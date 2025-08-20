import dataclasses as dc
import typing as ta

from omlish.manifests.globals import GlobalManifestLoader

from .base import Precheck
from .base import PrecheckContext


##


class ManifestsPrecheck(Precheck['ManifestsPrecheck.Config']):
    @dc.dataclass(frozen=True)
    class Config(Precheck.Config):
        pass

    def __init__(self, context: PrecheckContext, config: Config = Config()) -> None:
        super().__init__(config)

        self._context = context

    async def run(self) -> ta.AsyncGenerator[Precheck.Violation]:
        for src_root in sorted(self._context.src_roots):
            try:
                GlobalManifestLoader.load(packages=[src_root])
            except Exception as e:  # noqa
                yield Precheck.Violation(self, f'Error loading manifest for {src_root}: {e!r}')
