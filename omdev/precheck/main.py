"""
Tiny pre-commit

TODO:
 - define new prechecks with manifests
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
import argparse
import asyncio
import logging
import os.path
import sys
import typing as ta

from omlish import logs

from .base import Precheck
from .base import PrecheckContext
from .git import GitBlacklistPrecheck
from .lite import LitePython8Precheck
from .manifests import ManifestsPrecheck
from .scripts import ScriptDepsPrecheck


log = logging.getLogger(__name__)


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
        ManifestsPrecheck(ctx),
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
    parser_check.add_argument('-v', '--verbose', action='store_true')
    parser_check.set_defaults(func=_check_cmd)

    return parser


def _main(argv: ta.Sequence[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    logs.configure_standard_logging('DEBUG' if args.verbose else 'INFO')

    if not getattr(args, 'func', None):
        parser.print_help()
    else:
        args.func(args)


if __name__ == '__main__':
    _main()
