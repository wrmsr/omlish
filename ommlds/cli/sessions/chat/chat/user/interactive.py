import sys
import typing as ta

from ...... import minichain as mc
from ..... import asyncs
from .types import UserChatInput


##


class SyncStringInput(ta.Protocol):
    def __call__(self) -> str: ...


class InputSyncStringInput:
    DEFAULT_PROMPT: ta.ClassVar[str] = '> '

    def __init__(
            self,
            prompt: str | None = None,
            *,
            use_readline: bool | ta.Literal['auto'] = False,
    ) -> None:
        super().__init__()

        if prompt is None:
            prompt = self.DEFAULT_PROMPT
        self._prompt = prompt
        self._use_readline = use_readline

        self._handled_readline = False

    def _handle_readline(self) -> None:
        if self._handled_readline:
            return
        self._handled_readline = True

        if not self._use_readline:
            return

        if self._use_readline == 'auto':
            if not sys.stdin.isatty():
                return

        try:
            import readline  # noqa
        except ImportError:
            pass

    def __call__(self) -> str:
        self._handle_readline()
        return input(self._prompt)


#


class AsyncStringInput(ta.Protocol):
    def __call__(self) -> ta.Awaitable[str]: ...


class ThreadAsyncStringInput:
    def __init__(self, child: SyncStringInput, runner: asyncs.AsyncThreadRunner) -> None:
        super().__init__()

        self._child = child
        self._runner = runner

    async def __call__(self) -> str:
        return await self._runner.run_in_thread(self._child)


class SyncAsyncStringInput:
    def __init__(self, child: SyncStringInput) -> None:
        super().__init__()

        self._child = child

    async def __call__(self) -> str:
        return self._child()


##


class InteractiveUserChatInput(UserChatInput):
    DEFAULT_STRING_INPUT: ta.ClassVar[AsyncStringInput] = SyncAsyncStringInput(InputSyncStringInput())

    def __init__(
            self,
            string_input: AsyncStringInput | None = None,
    ) -> None:
        super().__init__()

        if string_input is None:
            string_input = self.DEFAULT_STRING_INPUT
        self._string_input = string_input

    async def get_next_user_messages(self) -> 'mc.UserChat':
        try:
            s = await self._string_input()
        except EOFError:
            return []
        return [mc.UserMessage(s)]
