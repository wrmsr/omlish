# ruff: noqa: UP006 UP007
"""
TODO:
 - interp
 - share more code with pyproject?
"""
import os.path
import typing as ta

from omlish.asyncs.asyncio.subprocesses import asyncio_subprocesses
from omlish.lite.cached import cached_nullary
from omlish.lite.check import check
from omlish.os.atomics import AtomicPathSwapping

from .paths import DeployPath
from .paths import DeployPathOwner
from .types import DeployAppTag
from .types import DeployHome


class DeployVenvManager(DeployPathOwner):
    def __init__(
            self,
            *,
            deploy_home: ta.Optional[DeployHome] = None,
            atomics: AtomicPathSwapping,
    ) -> None:
        super().__init__()

        self._deploy_home = deploy_home
        self._atomics = atomics

    @cached_nullary
    def _dir(self) -> str:
        return os.path.join(check.non_empty_str(self._deploy_home), 'venvs')

    def get_owned_deploy_paths(self) -> ta.AbstractSet[DeployPath]:
        return {
            DeployPath.parse('venvs/@app/@tag/'),
        }

    async def setup_venv(
            self,
            app_dir: str,
            venv_dir: str,
            *,
            use_uv: bool = True,
    ) -> None:
        sys_exe = 'python3'

        # !! NOTE: (most) venvs cannot be relocated, so an atomic swap can't be used. it's up to the path manager to
        # garbage collect orphaned dirs.
        await asyncio_subprocesses.check_call(sys_exe, '-m', 'venv', venv_dir)

        #

        venv_exe = os.path.join(venv_dir, 'bin', 'python3')

        #

        reqs_txt = os.path.join(app_dir, 'requirements.txt')

        if os.path.isfile(reqs_txt):
            if use_uv:
                await asyncio_subprocesses.check_call(venv_exe, '-m', 'pip', 'install', 'uv')
                pip_cmd = ['-m', 'uv', 'pip']
            else:
                pip_cmd = ['-m', 'pip']

            await asyncio_subprocesses.check_call(venv_exe, *pip_cmd,'install', '-r', reqs_txt)

    async def setup_app_venv(self, app_tag: DeployAppTag) -> None:
        await self.setup_venv(
            os.path.join(check.non_empty_str(self._deploy_home), 'apps', app_tag.app, app_tag.tag),
            os.path.join(self._dir(), app_tag.app, app_tag.tag),
        )
