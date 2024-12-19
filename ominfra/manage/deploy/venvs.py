# ruff: noqa: UP006 UP007
"""
TODO:
 - interp
 - share more code with pyproject?
"""
import os.path

from omdev.interp.resolvers import DEFAULT_INTERP_RESOLVER
from omdev.interp.types import InterpSpecifier
from omlish.asyncs.asyncio.subprocesses import asyncio_subprocesses
from omlish.lite.check import check

from .specs import DeployVenvSpec
from .types import DeployHome


class DeployVenvManager:
    async def setup_venv(
            self,
            spec: DeployVenvSpec,
            home: DeployHome,
            git_dir: str,
            venv_dir: str,
    ) -> None:
        if spec.interp is not None:
            i = InterpSpecifier.parse(check.not_none(spec.interp))
            o = check.not_none(await DEFAULT_INTERP_RESOLVER.resolve(i))
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
                await asyncio_subprocesses.check_call(venv_exe, '-m', 'pip', 'install', 'uv')
                pip_cmd = ['-m', 'uv', 'pip']
            else:
                pip_cmd = ['-m', 'pip']

            await asyncio_subprocesses.check_call(venv_exe, *pip_cmd,'install', '-r', reqs_txt)
