# ruff: noqa: UP006 UP007
import dataclasses as dc
import logging
import os.path
import typing as ta

from omlish.asyncs.asyncio.subprocesses import asyncio_subprocesses
from omlish.lite.cached import async_cached_nullary
from omlish.lite.cached import cached_nullary
from omlish.lite.check import check
from omlish.lite.typing import Func2

from .default import get_default_interp_resolver
from .types import InterpSpecifier


##


@dc.dataclass(frozen=True)
class InterpVenvConfig:
    interp: ta.Optional[str] = None
    requires: ta.Optional[ta.Sequence[str]] = None
    use_uv: ta.Optional[bool] = None


class InterpVenvRequirementsProcessor(Func2['InterpVenv', ta.Sequence[str], ta.Sequence[str]]):
    pass


class InterpVenv:
    def __init__(
            self,
            path: str,
            cfg: InterpVenvConfig,
            *,
            requirements_processor: ta.Optional[InterpVenvRequirementsProcessor] = None,
            log: ta.Optional[logging.Logger] = None,
    ) -> None:
        super().__init__()

        self._path = path
        self._cfg = cfg

        self._requirements_processor = requirements_processor
        self._log = log

    @property
    def path(self) -> str:
        return self._path

    @property
    def cfg(self) -> InterpVenvConfig:
        return self._cfg

    @async_cached_nullary
    async def interp_exe(self) -> str:
        i = InterpSpecifier.parse(check.not_none(self._cfg.interp))
        return check.not_none(await get_default_interp_resolver().resolve(i, install=True)).exe

    @cached_nullary
    def exe(self) -> str:
        ve = os.path.join(self._path, 'bin/python')
        if not os.path.isfile(ve):
            raise Exception(f'venv exe {ve} does not exist or is not a file!')
        return ve

    @async_cached_nullary
    async def create(self) -> bool:
        if os.path.exists(dn := self._path):
            if not os.path.isdir(dn):
                raise Exception(f'{dn} exists but is not a directory!')
            return False

        ie = await self.interp_exe()

        if self._log is not None:
            self._log.info('Using interpreter %s', ie)

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
            reqs = list(sr)
            if self._requirements_processor is not None:
                reqs = list(self._requirements_processor(self, reqs))

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
