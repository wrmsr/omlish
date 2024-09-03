"""
Tiny pre-commit

TODO:
 - global config
 - global analyses - FilesWithShebang
 - shebang files have no relative imports
 - parallelize (asyncio)
  - anyio? aiofiles? :| nonblock open().read()
 - debug log
 - omlish-lite - no non-lite deps, etc etc
 - omlish-script - no deps, shebang, executable, can be 3.12
 - big git files https://github.com/pre-commit/pre-commit-hooks?tab=readme-ov-file#check-added-large-files
 - https://github.com/pre-commit/pre-commit-hooks?tab=readme-ov-file#check-case-conflict
 - https://github.com/pre-commit/pre-commit-hooks?tab=readme-ov-file#check-symlinks
 - https://github.com/pre-commit/pre-commit-hooks?tab=readme-ov-file#detect-aws-credentials
 - https://github.com/pre-commit/pre-commit-hooks?tab=readme-ov-file#forbid-new-submodules
 - don't check in .o's (omdev.ext import hook is dumb w build dir)
"""
import abc
import argparse
import asyncio
import dataclasses as dc
import glob
import inspect
import logging
import os.path
import stat
import subprocess
import sys
import textwrap
import typing as ta

from omdev import findimports
from omdev import findmagic
from omlish import cached
from omlish import logs


T = ta.TypeVar('T')
PrecheckConfigT = ta.TypeVar('PrecheckConfigT', bound='Precheck.Config')


log = logging.getLogger(__name__)


##


@dc.dataclass(frozen=True, kw_only=True)
class PrecheckContext:
    src_roots: ta.Sequence[str]


##


class Precheck(abc.ABC, ta.Generic[PrecheckConfigT]):
    @dc.dataclass(frozen=True)
    class Config:
        pass

    def __init__(self, context: PrecheckContext, config: PrecheckConfigT) -> None:
        super().__init__()
        self._context = context
        self._config = config

    @dc.dataclass(frozen=True)
    class Violation:
        pc: 'Precheck'
        msg: str

    @abc.abstractmethod
    def run(self) -> ta.AsyncIterator[Violation]:
        raise NotImplementedError


##


class GitBlacklistPrecheck(Precheck['GitBlacklistPrecheck.Config']):
    """
    TODO:
     - globs
     - regex
    """

    @dc.dataclass(frozen=True)
    class Config(Precheck.Config):
        files: ta.Sequence[str] = (
            '.env',
            'secrets.yml',
        )

    def __init__(self, context: PrecheckContext, config: Config = Config()) -> None:
        super().__init__(context, config)

    async def run(self) -> ta.AsyncGenerator[Precheck.Violation, None]:
        for f in self._config.files:
            proc = await asyncio.create_subprocess_exec('git', 'status', '-s', f)
            await proc.communicate()
            if proc.returncode:
                yield Precheck.Violation(self, f)


##


class ScriptDepsPrecheck(Precheck['ScriptDepsPrecheck.Config']):
    @dc.dataclass(frozen=True)
    class Config(Precheck.Config):
        pass

    def __init__(self, context: PrecheckContext, config: Config = Config()) -> None:
        super().__init__(context, config)

    async def run(self) -> ta.AsyncGenerator[Precheck.Violation, None]:
        for fp in findmagic.find_magic(
                self._context.src_roots,
                ['# @omlish-script'],
                ['py'],
        ):
            if not (stat.S_IXUSR & os.stat(fp).st_mode):
                yield Precheck.Violation(self, f'script {fp} is not executable')

            with open(fp) as f:  # noqa  # FIXME
                src = f.read()

            if not src.startswith('#!/usr/bin/env python3\n'):
                yield Precheck.Violation(self, f'script {fp} lacks correct shebang')

            imps = findimports.find_imports(fp)
            deps = findimports.get_import_deps(imps)
            if deps:
                yield Precheck.Violation(self, f'script {fp} has deps: {deps}')


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
            '.venvs/8/bin/python',
            '-c',
            self._load_file_module_payload(),
            fp,
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
            '.venvs/8/bin/python',
            '-c',
            f'import {mod}',
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


##


def _check_cmd(args) -> None:
    if not os.path.isfile('pyproject.toml'):
        raise RuntimeError('must run in project root')

    ctx = PrecheckContext(
        src_roots=args.roots,
    )

    pcs: list[Precheck] = [
        GitBlacklistPrecheck(ctx),
        ScriptDepsPrecheck(ctx),
        LitePython8Precheck(ctx),
    ]

    async def run() -> list[Precheck.Violation]:
        vs: list[Precheck.Violation] = []

        for pc in pcs:
            async for v in pc.run():
                vs.append(v)
                print(v)

        return vs

    vs = asyncio.run(run())

    if vs:
        print(f'{len(vs)} violations found')
        sys.exit(1)


##


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers()

    parser_check = subparsers.add_parser('check')
    parser_check.add_argument('roots', nargs='+')
    parser_check.set_defaults(func=_check_cmd)

    return parser


def _main(argv: ta.Sequence[str] | None = None) -> None:
    logs.configure_standard_logging('INFO')

    parser = _build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, 'func', None):
        parser.print_help()
    else:
        args.func(args)


if __name__ == '__main__':
    _main()
