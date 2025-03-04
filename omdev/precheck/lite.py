import asyncio
import dataclasses as dc
import glob
import inspect
import logging
import os.path
import subprocess
import textwrap
import typing as ta

from omlish import cached
from omlish.subprocesses.wrap import subprocess_maybe_shell_wrap_exec

from .. import magic
from .base import Precheck
from .base import PrecheckContext


log = logging.getLogger(__name__)


##


class LitePython8Precheck(Precheck['LitePython8Precheck.Config']):
    @dc.dataclass(frozen=True)
    class Config(Precheck.Config):
        python: str = '.venvs/8/bin/python'
        concurrency: int = 4

    def __init__(self, context: PrecheckContext, config: Config = Config()) -> None:
        super().__init__(context, config)

    #

    @dc.dataclass(frozen=True)
    class _Target:
        path: str
        kind: ta.Literal['script', 'module']

    async def _collect_targets(self) -> list[_Target]:
        lst = []

        for fp in magic.find_magic_files(
                magic.PY_MAGIC_STYLE,
                self._context.src_roots,
                keys=['@omlish-lite'],
        ):
            with open(fp) as f:  # noqa  # FIXME
                src = f.read()

            is_script = '# @omlish-script' in src.splitlines()

            if is_script:
                lst.append(self._Target(fp, 'script'))

            elif fp.endswith('__init__.py'):
                for g in glob.glob(os.path.join(os.path.dirname(fp), '**/*.py'), recursive=True):
                    lst.append(self._Target(g, 'module'))

            else:
                lst.append(self._Target(fp, 'module'))

        return lst

    #

    @staticmethod
    def _load_file_module(fp: str) -> None:
        import os.path  # noqa
        import sys  # noqa
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

        sys.modules[mn] = mod

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
                self._config.python,
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

    async def _run_module(self, fp: str) -> list[Precheck.Violation]:
        vs: list[Precheck.Violation] = []

        mod = fp.rpartition('.')[0].replace(os.sep, '.')

        log.debug('%s: loading module %s', self.__class__.__name__, mod)

        proc = await asyncio.create_subprocess_exec(
            *subprocess_maybe_shell_wrap_exec(
                self._config.python,
                '-c',
                f'import {mod}',
            ),
            stderr=subprocess.PIPE,
        )

        _, stderr = await proc.communicate()
        if proc.returncode != 0:
            vs.append(Precheck.Violation(self, f'lite module {fp} failed to import in python8: {stderr.decode()}'))  # noqa

        return vs

    #

    async def _run_one(self, tgt: _Target) -> list[Precheck.Violation]:
        if tgt.kind == 'script':
            return await self._run_script(tgt.path)

        elif tgt.kind == 'module':
            return await self._run_module(tgt.path)

        else:
            raise RuntimeError(f'Unknown target kind: {tgt.kind}')

    async def run(self) -> ta.AsyncGenerator[Precheck.Violation, None]:
        tgts = await self._collect_targets()

        sem = asyncio.Semaphore(self._config.concurrency)

        async def run(tgt):
            async with sem:
                return await self._run_one(tgt)

        tasks = [asyncio.create_task(run(tgt)) for tgt in tgts]

        for coro in asyncio.as_completed(tasks):
            for v in await coro:
                yield v
