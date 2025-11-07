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
import os.path
import typing as ta

from omlish import inject as inj
from omlish.logs import all as logs

from .base import Precheck
from .base import PrecheckContext
from .blanklines import BlankLinesPrecheck
from .caches import AstCache
from .caches import DirWalkCache
from .caches import HeadersCache
from .caches import TextFileCache
from .caches import TokensCache
from .git import GitBlacklistPrecheck
from .imports import RootRelativeImportPrecheck
from .lite import LitePython8Precheck
from .manifests import ManifestsPrecheck
from .scripts import ScriptDepsPrecheck
from .unicode import UnicodePrecheck


log = logs.get_module_logger(globals())


##


def bind_main(
        ctx: PrecheckContext,
        pc_cfgs: ta.Iterable[Precheck.Config],
) -> inj.Elements:
    lst: list[inj.Elemental] = [
        inj.bind(ctx),

        inj.set_binder[Precheck](),

        inj.bind(AstCache, singleton=True),
        inj.bind(DirWalkCache, singleton=True),
        inj.bind(HeadersCache, singleton=True),
        inj.bind(TextFileCache, singleton=True),
        inj.bind(TokensCache, singleton=True),
    ]

    #

    for pc_cfg in pc_cfgs:
        lst.extend([
            inj.bind(pc_cfg),
            inj.bind(pc_cfg.configurable_cls, eager=True, singleton=True),
            inj.set_binder[Precheck]().bind(pc_cfg.configurable_cls),
        ])

    #

    return inj.as_elements(*lst)


def _check_cmd(args) -> None:
    if not os.path.isfile('pyproject.toml'):
        raise RuntimeError('must run in project root')

    ctx = PrecheckContext(
        src_roots=args.roots,
    )

    pc_cfgs: list[Precheck.Config] = [
        BlankLinesPrecheck.Config(),
        GitBlacklistPrecheck.Config(),
        LitePython8Precheck.Config(),
        ManifestsPrecheck.Config(),
        RootRelativeImportPrecheck.Config(),
        ScriptDepsPrecheck.Config(),
        UnicodePrecheck.Config(),
    ]

    with inj.create_managed_injector(bind_main(
        ctx,
        pc_cfgs,
    )) as injector:
        async def run() -> list[Precheck.Violation]:
            vs: list[Precheck.Violation] = []

            pcs = sorted(
                injector[ta.AbstractSet[Precheck]],
                key=lambda pc: type(pc).__name__,
            )

            for pc in pcs:
                log.info('Running precheck: %s', type(pc).__name__)
                async for v in pc.run():
                    vs.append(v)
                    print('*** VIOLATION ***')
                    print(f'Seq: {len(vs)}')
                    print(f'Precheck: {v.pc}')
                    print(f'Message:')
                    print(v.msg.strip())
                    print()

            return vs

        vs = asyncio.run(run())

        if vs:
            print(f'{len(vs)} violations found')
            raise SystemExit(1)


##


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true')

    subparsers = parser.add_subparsers()

    parser_check = subparsers.add_parser('check')
    parser_check.add_argument('roots', nargs='+')
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
