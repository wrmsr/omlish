#!/usr/bin/env python3
# @omlish-amalg ../scripts/interp.py
# ruff: noqa: UP007
"""
TODO:
 - partial best-matches - '3.12'
 - https://github.com/asdf-vm/asdf support (instead of pyenv) ?
 - colon sep provider name prefix - pyenv:3.12


"""
import argparse
import asyncio
import typing as ta

from omlish.argparse.cli import ArgparseCli
from omlish.argparse.cli import argparse_arg
from omlish.argparse.cli import argparse_command
from omlish.lite.check import check
from omlish.lite.runtime import check_lite_runtime_version
from omlish.logs.standard import configure_standard_logging

from .resolvers import DEFAULT_INTERP_RESOLVER
from .resolvers import INTERP_PROVIDER_TYPES_BY_NAME
from .resolvers import InterpResolver
from .types import InterpSpecifier


class InterpCli(ArgparseCli):
    @argparse_command(
        argparse_arg('version'),
        argparse_arg('-d', '--debug', action='store_true'),
    )
    async def list(self) -> None:
        r = DEFAULT_INTERP_RESOLVER
        s = InterpSpecifier.parse(args.version)
        await r.list(s)

    @argparse_command(
        argparse_arg('version'),
        argparse_arg('-p', '--provider'),
        argparse_arg('-d', '--debug', action='store_true'),
        argparse_arg('-i', '--install', action='store_true'),
    )
    async def resolve(self) -> None:
        if args.provider:
            p = INTERP_PROVIDER_TYPES_BY_NAME[args.provider]()
            r = InterpResolver([(p.name, p)])
        else:
            r = DEFAULT_INTERP_RESOLVER
        s = InterpSpecifier.parse(args.version)
        print(check.not_none(await r.resolve(s, install=bool(args.install))).exe)


async def _async_main(argv: ta.Optional[ta.Sequence[str]] = None) -> None:
    check_lite_runtime_version()
    configure_standard_logging()

    parser = _build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, 'func', None):
        parser.print_help()
    else:
        await args.func(args)


def _main(argv: ta.Optional[ta.Sequence[str]] = None) -> None:
    asyncio.run(_async_main(argv))


if __name__ == '__main__':
    _main()
