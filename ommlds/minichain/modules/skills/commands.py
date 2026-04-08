from omlish.argparse import all as argparse

from ...facades.commands.base import Command
from ...facades.text import FacadeText
from .manager import SkillsManager


##


class SkillsCommand(Command):
    def __init__(
            self,
            *,
            manager: SkillsManager,
    ) -> None:
        super().__init__()

        self._manager = manager

    async def _run_args(self, ctx: Command.Context, args: argparse.Namespace) -> None:
        skills = await self._manager.get_skills()

        parts: list[FacadeText] = []
        for sk in skills.values():
            parts.append(FacadeText.of(sk.name))

        await ctx.print(FacadeText.join('\n', parts))


##


class SkillCommand(Command):
    def __init__(
            self,
            *,
            manager: SkillsManager,
    ) -> None:
        super().__init__()

        self._manager = manager

    def _configure_parser(self, parser: argparse.ArgumentParser) -> None:
        super()._configure_parser(parser)

        parser.add_argument('name')
        parser.add_argument('args', nargs='?')

    async def _run_args(self, ctx: Command.Context, args: argparse.Namespace) -> None:
        sk = (await self._manager.get_skills())[args.name]  # noqa

        raise NotImplementedError
