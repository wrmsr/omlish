import asyncio
import dataclasses as dc
import typing as ta

from .base import Precheck
from .base import PrecheckContext


##


class GitBlacklistPrecheck(Precheck['GitBlacklistPrecheck.Config']):
    """
    TODO:
     - globs
     - regex
    """

    @dc.dataclass(frozen=True)
    class Config(Precheck.Config):
        files: ta.Sequence[str] = (
            '.env',
            'secrets.yml',
        )

    def __init__(self, context: PrecheckContext, config: Config = Config()) -> None:
        super().__init__(context, config)

    async def run(self) -> ta.AsyncGenerator[Precheck.Violation, None]:
        for f in self._config.files:
            proc = await asyncio.create_subprocess_exec('git', 'status', '-s', f)
            await proc.communicate()
            if proc.returncode:
                yield Precheck.Violation(self, f)
