# ruff: noqa: UP006 UP007
"""
TODO:
 - interp
 - share more code with pyproject?
"""
import os.path
import typing as ta

from omlish.lite.asyncio.subprocesses import asyncio_subprocess_check_call

from .paths import DeployPath
from .paths import DeployPathOwner
from .types import DeployAppTag
from .types import DeployHome


class DeployVenvManager(DeployPathOwner):
    def __init__(
            self,
            deploy_home: DeployHome,
    ) -> None:
        super().__init__()

        self._deploy_home = deploy_home
        self._dir = os.path.join(deploy_home, 'venvs')

    def get_deploy_paths(self) -> ta.AbstractSet[DeployPath]:
        return {
            DeployPath.parse('venvs/@app/@tag/'),
        }

    async def setup_venv(self, app_dir: str, venv_dir: str) -> None:
        sys_exe = 'python3'

        await asyncio_subprocess_check_call(sys_exe, '-m', 'venv', venv_dir)

        venv_exe = os.path.join(venv_dir, 'bin', 'python3')

        reqs_txt = os.path.join(app_dir, 'requirements.txt')
        if os.path.isfile(reqs_txt):
            await asyncio_subprocess_check_call(venv_exe, '-m', 'pip', 'install', '-r', reqs_txt)

    async def setup_app_venv(self, app_tag: DeployAppTag) -> None:
        await self.setup_venv(
            os.path.join(self._deploy_home, 'apps', app_tag.app, app_tag.tag),
            os.path.join(self._deploy_home, 'venvs', app_tag.app, app_tag.tag),
        )
