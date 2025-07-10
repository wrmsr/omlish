# ruff: noqa: UP006 UP007 UP045
"""
TODO:
 - interp
 - share more code with pyproject?
"""
import os.path
import shutil

from omdev.interp.default import get_default_interp_resolver
from omdev.interp.types import InterpSpecifier
from omlish.asyncs.asyncio.subprocesses import asyncio_subprocesses
from omlish.lite.check import check

from .specs import DeployVenvSpec


##


class DeployVenvManager:
    async def setup_venv(
            self,
            spec: DeployVenvSpec,
            git_dir: str,
            venv_dir: str,
    ) -> None:
        if spec.interp is not None:
            i = InterpSpecifier.parse(check.not_none(spec.interp))
            o = check.not_none(await get_default_interp_resolver().resolve(i))
            sys_exe = o.exe
        else:
            sys_exe = 'python3'

        #

        # !! NOTE: (most) venvs cannot be relocated, so an atomic swap can't be used. it's up to the path manager to
        # garbage collect orphaned dirs.
        await asyncio_subprocesses.check_call(sys_exe, '-m', 'venv', venv_dir)

        #

        venv_exe = os.path.join(venv_dir, 'bin', 'python3')

        #

        reqs_txt = os.path.join(git_dir, 'requirements.txt')

        if os.path.isfile(reqs_txt):
            if spec.use_uv:
                if shutil.which('uv') is not None:
                    pip_cmd = ['uv', 'pip']
                else:
                    await asyncio_subprocesses.check_call(venv_exe, '-m', 'pip', 'install', 'uv')
                    pip_cmd = [venv_exe, '-m', 'uv', 'pip']
            else:
                pip_cmd = [venv_exe, '-m', 'pip']

            await asyncio_subprocesses.check_call(*pip_cmd, 'install', '-r', reqs_txt, cwd=venv_dir)
