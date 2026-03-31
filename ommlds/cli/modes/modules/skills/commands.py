from omlish.argparse import all as argparse

from ..... import minichain as mc


##


class SkillCommand(mc.facades.Command):
    def _configure_parser(self, parser: argparse.ArgumentParser) -> None:
        super()._configure_parser(parser)

        parser.add_argument('args')

    async def _run_args(self, ctx: mc.facades.Command.Context, args: argparse.Namespace) -> None:
        raise NotImplementedError
