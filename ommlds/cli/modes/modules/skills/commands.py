from omlish.argparse import all as argparse

from ...chat.facades.commands.base import Command


##


class SkillCommand(Command):
    def _configure_parser(self, parser: argparse.ArgumentParser) -> None:
        super()._configure_parser(parser)

        parser.add_argument('args')

    async def _run_args(self, ctx: Command.Context, args: argparse.Namespace) -> None:
        raise NotImplementedError
