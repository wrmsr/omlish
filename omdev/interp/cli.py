# @omlish-amalg ../scripts/interp.py
# ruff: noqa: UP007
"""
TODO:
 - partial best-matches - '3.12'
 - https://github.com/asdf-vm/asdf support (instead of pyenv) ?
 - colon sep provider name prefix - pyenv:3.12
"""
import asyncio
import typing as ta

from omlish.argparse.cli import ArgparseCli
from omlish.argparse.cli import argparse_arg
from omlish.argparse.cli import argparse_cmd
from omlish.lite.cached import cached_nullary
from omlish.lite.check import check
from omlish.lite.inject import Injector
from omlish.lite.inject import inj
from omlish.lite.runtime import check_lite_runtime_version
from omlish.logs.standard import configure_standard_logging

from .inject import bind_interp
from .resolvers import InterpResolver
from .resolvers import InterpResolverProviders
from .types import InterpSpecifier


class InterpCli(ArgparseCli):
    @cached_nullary
    def injector(self) -> Injector:
        return inj.create_injector(bind_interp())

    @cached_nullary
    def providers(self) -> InterpResolverProviders:
        return self.injector()[InterpResolverProviders]

    #

    @argparse_cmd(
        argparse_arg('version'),
        argparse_arg('-d', '--debug', action='store_true'),
    )
    async def list(self) -> None:
        r = InterpResolver(self.providers())
        s = InterpSpecifier.parse(self.args.version)
        await r.list(s)

    @argparse_cmd(
        argparse_arg('version'),
        argparse_arg('-p', '--provider'),
        argparse_arg('-d', '--debug', action='store_true'),
        argparse_arg('-i', '--install', action='store_true'),
    )
    async def resolve(self) -> None:
        if self.args.provider:
            p = check.single([p for n, p in self.providers().providers if n == self.args.provider])
            r = InterpResolver(InterpResolverProviders([(p.name, p)]))
        else:
            r = InterpResolver(self.providers())
        s = InterpSpecifier.parse(self.args.version)
        print(check.not_none(await r.resolve(s, install=bool(self.args.install))).exe)


async def _async_main(argv: ta.Optional[ta.Sequence[str]] = None) -> None:
    check_lite_runtime_version()
    configure_standard_logging()

    cli = InterpCli(argv)
    await cli.async_cli_run()


def _main(argv: ta.Optional[ta.Sequence[str]] = None) -> None:
    asyncio.run(_async_main(argv))


if __name__ == '__main__':
    _main()
