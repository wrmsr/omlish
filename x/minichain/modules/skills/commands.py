from omcore.argparse import all as argparse

from ...facades.commands.base import Command
from ...ui.text import UiText
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

        parts: list[UiText] = []
        for sk in skills.values():
            parts.append(UiText.of(sk.name))

        await ctx.print(UiText.join('\n', parts))


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
