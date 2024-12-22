# ruff: noqa: UP006 UP007
import dataclasses as dc
import logging
import os.path
import shutil
import sys
import tempfile
import typing as ta

from omlish.asyncs.asyncio.subprocesses import asyncio_subprocesses
from omlish.lite.cached import async_cached_nullary
from omlish.lite.check import check


@dc.dataclass(frozen=True)
class UvConfig:
    ignore_path: bool = False
    pip_bootstrap: bool = True


class Uv:
    def __init__(
            self,
            config: UvConfig = UvConfig(),
            *,
            log: ta.Optional[logging.Logger] = None,
    ) -> None:
        super().__init__()

        self._config = config
        self._log = log

        self._bootstrap_dir: ta.Optional[str] = None

    def delete_bootstrap_dir(self) -> bool:
        if (bs := self._bootstrap_dir) is None:
            return False

        shutil.rmtree(bs)
        self._bootstrap_dir = None
        return True

    @async_cached_nullary
    async def uv_exe(self) -> ta.Optional[str]:
        if not self._config.ignore_path and (uv := shutil.which('uv')):
            return uv

        if self._config.pip_bootstrap:
            if (bd := self._bootstrap_dir) is None:
                bd = self._bootstrap_dir = tempfile.mkdtemp()

            if self._log is not None:
                self._log.info(f'Bootstrapping uv into %s', bd)

            vn = 'uv-bootstrap'
            await asyncio_subprocesses.check_call(os.path.realpath(sys.executable), '-m', 'venv', vn, cwd=bd)

            vx = os.path.join(bd, vn, 'bin', 'python3')
            await asyncio_subprocesses.check_call(vx, '-m', 'pip', 'install', 'uv', cwd=bd)

            ux = os.path.join(bd, vn, 'bin', 'uv')
            check.state(os.path.isfile(ux))

            return ux

        return None
