"""
Tiny pre-commit

TODO:
 - global config
 - global analyses - FilesWithShebang
 - shebang files have no relative imports
 - parallelize (asyncio)
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
import dataclasses as dc
import glob
import inspect
import logging
import os.path
import stat
import subprocess
import textwrap
import typing as ta

from omdev import findimports
from omdev import findmagic
from omlish import cached


T = ta.TypeVar('T')
PrecheckConfigT = ta.TypeVar('PrecheckConfigT', bound='Precheck.Config')


log = logging.getLogger(__name__)


##


class Precheck(abc.ABC, ta.Generic[PrecheckConfigT]):
    @dc.dataclass(frozen=True)
    class Config:
        pass

    def __init__(self, config: PrecheckConfigT) -> None:
        super().__init__()
        self._config = config

    @dc.dataclass(frozen=True)
    class Violation:
        pc: 'Precheck'
        msg: str

    @abc.abstractmethod
    def run(self) -> ta.Iterable[Violation]:
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

    def __init__(self, config: Config = Config()) -> None:
        super().__init__(config)

    def run(self) -> ta.Iterable[Precheck.Violation]:
        for f in self._config.files:
            if subprocess.check_output(['git',  'status', '-s', f]):
                yield Precheck.Violation(self, f)


##


class ScriptDepsPrecheck(Precheck['ScriptDepsPrecheck.Config']):
    """
    TODO:
     - global/run config, ${SRCS}
    """

    @dc.dataclass(frozen=True)
    class Config(Precheck.Config):
        roots: ta.Sequence[str] = (
            'omdev',
            'ominfra',
            'omlish',
            'ommlx',
            'omserv',
        )

    def __init__(self, config: Config = Config()) -> None:
        super().__init__(config)

    def run(self) -> ta.Iterable[Precheck.Violation]:
        for fp in findmagic.find_magic(
                self._config.roots,
                ['# @omlish-script'],
                ['py'],
        ):
            if not (stat.S_IXUSR & os.stat(fp).st_mode):
                yield Precheck.Violation(self, f'script {fp} is not executable')

            with open(fp) as f:
                src = f.read()

            if not src.startswith('#!/usr/bin/env python3\n'):
                yield Precheck.Violation(self, f'script {fp} lacks correct shebang')

            imps = findimports.find_imports(fp)
            deps = findimports.get_import_deps(imps)
            if deps:
                yield Precheck.Violation(self, f'script {fp} has deps: {deps}')


##


class LitePython8Precheck(Precheck['LitePy8Precheck.Config']):
    @dc.dataclass(frozen=True)
    class Config(Precheck.Config):
        roots: ta.Sequence[str] = (
            'omdev',
            'ominfra',
            'omlish',
            'ommlx',
            'omserv',
        )

    def __init__(self, config: Config = Config()) -> None:
        super().__init__(config)

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
        mod.__builtins__ = __builtins__
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

    def run(self) -> ta.Iterable[Precheck.Violation]:
        for fp in findmagic.find_magic(
                self._config.roots,
                ['# @omlish-lite'],
                ['py'],
        ):
            with open(fp) as f:
                src = f.read()

            is_script = '# @omlish-script' in src.splitlines()

            if is_script:
                log.info('%s: loading script %s', self.__class__.__name__, fp)

                proc = subprocess.Popen(
                    [
                        '.venvs/8/bin/python',
                        '-c',
                        self._load_file_module_payload(),
                        fp,
                    ],
                    stderr=subprocess.PIPE,
                )

                _, stderr = proc.communicate()
                if proc.returncode != 0:
                    yield Precheck.Violation(self, f'lite script {fp} failed to load in python8: {stderr.decode()}')

            else:
                if fp.endswith('__init__.py'):
                    pfps = glob.glob(os.path.join(os.path.dirname(fp), '**/*.py'), recursive=True)
                else:
                    pfps = [fp]

                for pfp in pfps:
                    mod = pfp.rpartition('.')[0].replace(os.sep, '.')

                    log.info('%s: loading module %s', self.__class__.__name__, mod)

                    proc = subprocess.Popen(
                        [
                            '.venvs/8/bin/python',
                            '-c',
                            f'import {mod}',
                        ],
                        stderr=subprocess.PIPE,
                    )

                    _, stderr = proc.communicate()
                    if proc.returncode != 0:
                        yield Precheck.Violation(self, f'lite module {pfp} failed to import in python8: {stderr.decode()}')  # noqa


##


def _check_cmd(args) -> None:
    if not os.path.isfile('pyproject.toml'):
        raise RuntimeError('must run in project root')

    pcs: list[Precheck] = [
        GitBlacklistPrecheck(),
        ScriptDepsPrecheck(),
        LitePython8Precheck(),
    ]

    vs: list[Precheck.Violation] = []

    for pc in pcs:
        for v in pc.run():
            vs.append(v)
            print(v)

    if vs:
        print(f'{len(vs)} violations found')
        exit(1)


##


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers()

    parser_resolve = subparsers.add_parser('check')
    parser_resolve.set_defaults(func=_check_cmd)

    return parser


def _main(argv: ta.Optional[ta.Sequence[str]] = None) -> None:
    logging.root.addHandler(logging.StreamHandler())
    logging.root.setLevel('INFO')

    parser = _build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, 'func', None):
        parser.print_help()
    else:
        args.func(args)


if __name__ == '__main__':
    _main()
