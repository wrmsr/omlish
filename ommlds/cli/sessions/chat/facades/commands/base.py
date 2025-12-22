import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang
from omlish.argparse import all as argparse


##


class CommandError(Exception):
    pass


@dc.dataclass(frozen=True)
class ArgsCommandError(CommandError):
    command: 'Command'
    argv: ta.Sequence[str]
    help: str

    arg_error: argparse.ArgumentError | None = None


##


class Command(lang.Abstract):
    def __init__(self) -> None:
        super().__init__()

        self.__parser: argparse.ArgumentParser = argparse.NoExitArgumentParser(
            prog=self.name,
            description=self.description,
            formatter_class=self._HelpFormatter,
        )
        self._configure_parser(self.__parser)

    #

    @property
    def name(self) -> str:
        return lang.camel_to_snake(type(self).__name__.removesuffix('Command'))

    @property
    def description(self) -> str | None:
        return None

    class _HelpFormatter(argparse.HelpFormatter):
        def start_section(self, heading):
            return super().start_section(heading.title())

        def add_usage(self, usage, actions, groups, prefix=None):
            if prefix is None:
                prefix = 'Usage: '
            return super().add_usage(usage, actions, groups, prefix)

    def _configure_parser(self, parser: argparse.ArgumentParser) -> None:
        pass

    #

    @dc.dataclass(frozen=True, kw_only=True)
    class Context:
        print: ta.Callable[[str], ta.Awaitable[None]]

    @ta.final
    async def run(self, ctx: Context, argv: list[str]) -> None:
        try:
            args = self.__parser.parse_args(argv)
        except argparse.ArgumentError as ae:
            raise ArgsCommandError(
                self,
                argv,
                self.__parser.format_help(),
                ae,
            ) from ae

        await self._run_args(ctx, args)

    @abc.abstractmethod
    def _run_args(self, ctx: Context, args: argparse.Namespace) -> ta.Awaitable[None]:
        raise NotImplementedError
