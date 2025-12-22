import typing as ta

from omlish import lang
from omlish.argparse import all as argparse


##


class QuitSignal(lang.Func0[ta.Awaitable[None]]):
    pass


class QuitCommand:
    def __init__(
            self,
            *,
            quit_signal: QuitSignal,
    ) -> None:
        super().__init__()

        self._quit_signal = quit_signal

    async def _run_args(self, args: argparse.Namespace) -> None:
        await self._quit_signal()
