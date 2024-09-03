"""
Tiny pre-commit

TODO:
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
import logging
import os.path
import stat
import subprocess
import typing as ta

from omdev import findimports
from omdev import findmagic


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


def _check_cmd(args) -> None:
    if not os.path.isfile('pyproject.toml'):
        raise RuntimeError('must run in project root')

    vs: list[Precheck.Violation] = []

    for pc in [
        GitBlacklistPrecheck(),
        ScriptDepsPrecheck(),
    ]:
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
