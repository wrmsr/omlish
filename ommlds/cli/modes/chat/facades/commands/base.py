import abc
import contextvars
import typing as ta

from omlish import dataclasses as dc
from omlish import lang
from omlish.argparse import all as ap

from ..text import CanFacadeText


##


class CommandError(Exception):
    pass


@dc.dataclass()
class ArgsCommandError(CommandError):
    command: 'Command'
    argv: ta.Sequence[str]
    help: str

    arg_error: ap.ArgumentError | None = None


##


PRINTED_MESSAGES_CV: contextvars.ContextVar[list[str]] = contextvars.ContextVar(f'{__name__}.PRINTED_MESSAGES_CV')


class Command(lang.Abstract):
    def __init__(self) -> None:
        super().__init__()

        self.__parser: Command._ArgumentParser = self._ArgumentParser(
            prog=self.name,
            description=self.description,
            formatter_class=self._HelpFormatter,
        )
        self._configure_parser(self.__parser)

    #

    class _ArgumentParser(ap.NoExitArgumentParser):
        def _print_message(self, message, file=None):
            if message:
                PRINTED_MESSAGES_CV.get().append(message)

        def exit(self, status=0, message=None):
            if message:
                PRINTED_MESSAGES_CV.get().append(message)

            super().exit(status, message)

    #

    @property
    def name(self) -> str:
        return lang.camel_to_snake(type(self).__name__.removesuffix('Command'))

    @property
    def description(self) -> str | None:
        return None

    class _HelpFormatter(ap.HelpFormatter):
        def start_section(self, heading):
            return super().start_section(heading.title())

        def add_usage(self, usage, actions, groups, prefix=None):
            if prefix is None:
                prefix = 'Usage: '
            return super().add_usage(usage, actions, groups, prefix)

    def _configure_parser(self, parser: ap.ArgumentParser) -> None:
        pass

    #

    @dc.dataclass(frozen=True, kw_only=True)
    class Context:
        print: ta.Callable[[CanFacadeText], ta.Awaitable[None]]

    @ta.final
    async def run(self, ctx: Context, argv: list[str]) -> None:
        pm: list[str] = []

        args: ap.Namespace | None

        with lang.context_var_setting(PRINTED_MESSAGES_CV, pm):
            try:
                args = self.__parser.parse_args(argv)

            except ap.NoExitArgumentParser.ExitNotSupportedError:
                args = None

            except ap.ArgumentError as ae:
                raise ArgsCommandError(
                    self,
                    argv,
                    self.__parser.format_help(),
                    ae,
                ) from ae

        if pm:
            await ctx.print('\n'.join(pm))

        if args is not None:
            await self._run_args(ctx, args)

    @abc.abstractmethod
    def _run_args(self, ctx: Context, args: ap.Namespace) -> ta.Awaitable[None]:
        raise NotImplementedError
