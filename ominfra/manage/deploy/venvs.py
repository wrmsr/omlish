# ruff: noqa: UP006 UP007
"""
TODO:
 - interp
 - share more code with pyproject?
"""
import os.path

from omlish.asyncs.asyncio.subprocesses import asyncio_subprocesses
from omlish.os.atomics import AtomicPathSwapping

from .specs import DeployVenvSpec


class DeployVenvManager:
    def __init__(
            self,
            *,
            atomics: AtomicPathSwapping,
    ) -> None:
        super().__init__()

        self._atomics = atomics

    async def setup_venv(
            self,
            spec: DeployVenvSpec,
            git_dir: str,
            venv_dir: str,
    ) -> None:
        sys_exe = 'python3'

        # !! NOTE: (most) venvs cannot be relocated, so an atomic swap can't be used. it's up to the path manager to
        # garbage collect orphaned dirs.
        await asyncio_subprocesses.check_call(sys_exe, '-m', 'venv', venv_dir)

        #

        venv_exe = os.path.join(venv_dir, 'bin', 'python3')

        #

        reqs_txt = os.path.join(git_dir, 'requirements.txt')

        if os.path.isfile(reqs_txt):
            if spec.use_uv:
                await asyncio_subprocesses.check_call(venv_exe, '-m', 'pip', 'install', 'uv')
                pip_cmd = ['-m', 'uv', 'pip']
            else:
                pip_cmd = ['-m', 'pip']

            await asyncio_subprocesses.check_call(venv_exe, *pip_cmd,'install', '-r', reqs_txt)
