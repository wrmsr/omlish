from omlish.argparse import all as argparse

from ..input import UserInputSenderGetter
from .base import Command


##


class SendCommand(Command):
    def __init__(
            self,
            *,
            user_input_sender: UserInputSenderGetter,
    ) -> None:
        super().__init__()

        self._user_input_sender = user_input_sender

    def _configure_parser(self, parser: argparse.ArgumentParser) -> None:
        super()._configure_parser(parser)

        parser.add_argument('-q', '--quiet', action='store_true')
        parser.add_argument('message')

    async def _run_args(self, ctx: Command.Context, args: argparse.Namespace) -> None:
        await (await self._user_input_sender()).send_user_input(
            args.message,
            no_echo=args.quiet,
        )
