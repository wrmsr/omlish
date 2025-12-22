import typing as ta

from omlish import lang
from omlish.argparse import all as argparse

from .base import Command


##


class EchoCommand(Command):
    def _configure_parser(self, parser: argparse.ArgumentParser) -> None:
        super()._configure_parser(parser)

        parser.add_argument('message', help='Message to echo')

    async def _run_args(self, ctx: Command.Context, args: argparse.Namespace) -> None:
        await ctx.print(args.message)


##


class QuitSignal(lang.Func0[ta.Awaitable[None]]):
    pass


class QuitCommand(Command):
    def __init__(
            self,
            *,
            quit_signal: QuitSignal,
    ) -> None:
        super().__init__()

        self._quit_signal = quit_signal

    async def _run_args(self, ctx: Command.Context, args: argparse.Namespace) -> None:
        await self._quit_signal()
