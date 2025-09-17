# ruff: noqa: UP006 UP007 UP045
import glob
import os.path
import re
import typing as ta

from omlish.lite.cached import async_cached_nullary
from omlish.lite.cached import cached_nullary
from omlish.logs.modules import get_module_logger

from ..interp.venvs import InterpVenv
from ..interp.venvs import InterpVenvRequirementsProcessor
from .configs import VenvConfig
from .reqs import RequirementsRewriter


log = get_module_logger(globals())  # noqa


##


class Venv:
    def __init__(
            self,
            name: str,
            cfg: VenvConfig,
    ) -> None:
        super().__init__()

        self._name = name
        self._cfg = cfg

    @property
    def cfg(self) -> VenvConfig:
        return self._cfg

    DIR_NAME = '.venvs'

    @property
    def dir_name(self) -> str:
        return os.path.join(self.DIR_NAME, self._name)

    @cached_nullary
    def _iv(self) -> InterpVenv:
        rr = RequirementsRewriter(
            venv=self._name,
            only_pats=(
                [re.compile(p) for p in self._cfg.requires_pats]
                if self._cfg.requires_pats is not None else None
            ),
        )

        return InterpVenv(
            self.dir_name,
            self._cfg,
            requirements_processor=InterpVenvRequirementsProcessor(
                lambda iv, reqs: [rr.rewrite(req) for req in reqs]  # noqa
            ),
            log=log,
        )

    @cached_nullary
    def exe(self) -> str:
        return self._iv().exe()

    @async_cached_nullary
    async def create(self) -> bool:
        return await self._iv().create()

    @staticmethod
    def _resolve_srcs(raw: ta.List[str]) -> ta.List[str]:
        out: list[str] = []
        seen: ta.Set[str] = set()
        for r in raw:
            es: list[str]
            if any(c in r for c in '*?'):
                es = list(glob.glob(r, recursive=True))
            else:
                es = [r]
            for e in es:
                if e not in seen:
                    seen.add(e)
                    out.append(e)
        return out

    @cached_nullary
    def srcs(self) -> ta.Sequence[str]:
        return self._resolve_srcs(self._cfg.srcs or [])
