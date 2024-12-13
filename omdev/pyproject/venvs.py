# ruff: noqa: UP006 UP007
import glob
import os.path
import typing as ta

from omlish.asyncs.asyncio.subprocesses import asyncio_subprocesses
from omlish.lite.cached import async_cached_nullary
from omlish.lite.cached import cached_nullary
from omlish.lite.check import check
from omlish.lite.logs import log

from ..interp.resolvers import DEFAULT_INTERP_RESOLVER
from ..interp.types import InterpSpecifier
from .configs import VenvConfig
from .reqs import RequirementsRewriter


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

    @async_cached_nullary
    async def interp_exe(self) -> str:
        i = InterpSpecifier.parse(check.not_none(self._cfg.interp))
        return check.not_none(await DEFAULT_INTERP_RESOLVER.resolve(i, install=True)).exe

    @cached_nullary
    def exe(self) -> str:
        ve = os.path.join(self.dir_name, 'bin/python')
        if not os.path.isfile(ve):
            raise Exception(f'venv exe {ve} does not exist or is not a file!')
        return ve

    @async_cached_nullary
    async def create(self) -> bool:
        if os.path.exists(dn := self.dir_name):
            if not os.path.isdir(dn):
                raise Exception(f'{dn} exists but is not a directory!')
            return False

        log.info('Using interpreter %s', (ie := await self.interp_exe()))
        await asyncio_subprocesses.check_call(ie, '-m', 'venv', dn)

        ve = self.exe()
        uv = self._cfg.use_uv

        await asyncio_subprocesses.check_call(
            ve,
            '-m', 'pip',
            'install', '-v', '--upgrade',
            'pip',
            'setuptools',
            'wheel',
            *(['uv'] if uv else []),
        )

        if sr := self._cfg.requires:
            rr = RequirementsRewriter(self._name)
            reqs = [rr.rewrite(req) for req in sr]

            # TODO: automatically try slower uv download when it fails? lol
            #   Caused by: Failed to download distribution due to network timeout. Try increasing UV_HTTP_TIMEOUT (current value: 30s).  # noqa
            #   UV_CONCURRENT_DOWNLOADS=4 UV_HTTP_TIMEOUT=3600

            await asyncio_subprocesses.check_call(
                ve,
                '-m',
                *(['uv'] if uv else []),
                'pip',
                'install',
                *([] if uv else ['-v']),
                *reqs,
            )

        return True

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
