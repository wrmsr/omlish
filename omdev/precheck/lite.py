import asyncio
import dataclasses as dc
import glob
import inspect
import logging
import os.path
import subprocess
import textwrap
import typing as ta

from omdev import findmagic
from omlish import cached
from omlish.lite.subprocesses import subprocess_maybe_shell_wrap_exec

from .base import Precheck
from .base import PrecheckContext


log = logging.getLogger(__name__)


##


class LitePython8Precheck(Precheck['LitePython8Precheck.Config']):
    @dc.dataclass(frozen=True)
    class Config(Precheck.Config):
        pass

    def __init__(self, context: PrecheckContext, config: Config = Config()) -> None:
        super().__init__(context, config)

    #

    @staticmethod
    def _load_file_module(fp: str) -> None:
        import os.path  # noqa
        import types  # noqa

        fp = os.path.abspath(fp)

        with open(fp) as f:
            src = f.read()

        mn = os.path.basename(fp).rpartition('.')[0]

        mod = types.ModuleType(mn)
        mod.__name__ = mn
        mod.__file__ = fp
        mod.__builtins__ = __builtins__  # type: ignore
        mod.__spec__ = None

        code = compile(src, fp, 'exec')
        exec(code, mod.__dict__, mod.__dict__)

    @cached.function
    def _load_file_module_payload(self) -> str:
        return '\n'.join([
            'import sys',
            'fp = sys.argv[-1]',
            '',
            textwrap.dedent('\n'.join(inspect.getsource(LitePython8Precheck._load_file_module).splitlines()[2:])),
        ])

    #

    async def _run_script(self, fp: str) -> list[Precheck.Violation]:
        log.debug('%s: loading script %s', self.__class__.__name__, fp)

        vs: list[Precheck.Violation] = []

        proc = await asyncio.create_subprocess_exec(
            *subprocess_maybe_shell_wrap_exec(
                '.venvs/8/bin/python',
                '-c',
                self._load_file_module_payload(),
                fp,
            ),
            stderr=subprocess.PIPE,
        )

        _, stderr = await proc.communicate()
        if proc.returncode != 0:
            vs.append(Precheck.Violation(self, f'lite script {fp} failed to load in python8: {stderr.decode()}'))

        return vs

    async def _run_one_module(self, fp: str) -> list[Precheck.Violation]:
        vs: list[Precheck.Violation] = []

        mod = fp.rpartition('.')[0].replace(os.sep, '.')

        log.debug('%s: loading module %s', self.__class__.__name__, mod)

        proc = await asyncio.create_subprocess_exec(
            *subprocess_maybe_shell_wrap_exec(
                '.venvs/8/bin/python',
                '-c',
                f'import {mod}',
            ),
            stderr=subprocess.PIPE,
        )

        _, stderr = await proc.communicate()
        if proc.returncode != 0:
            vs.append(Precheck.Violation(self, f'lite module {fp} failed to import in python8: {stderr.decode()}'))  # noqa

        return vs

    async def _run_module(self, fp: str) -> list[Precheck.Violation]:
        vs: list[Precheck.Violation] = []

        if fp.endswith('__init__.py'):
            pfps = glob.glob(os.path.join(os.path.dirname(fp), '**/*.py'), recursive=True)
        else:
            pfps = [fp]

        for pfp in pfps:
            vs.extend(await self._run_one_module(pfp))

        return vs

    async def run(self) -> ta.AsyncGenerator[Precheck.Violation, None]:
        for fp in findmagic.find_magic(
                self._context.src_roots,
                ['# @omlish-lite'],
                ['py'],
        ):
            with open(fp) as f:  # noqa  # FIXME
                src = f.read()

            is_script = '# @omlish-script' in src.splitlines()

            if is_script:
                for v in await self._run_script(fp):
                    yield v

            else:
                for v in await self._run_module(fp):
                    yield v
