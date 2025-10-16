import functools
import typing as ta

from omlish import lang

from ...... import minichain as mc
from .types import UserChatInput


##


class InteractiveUserChatInput(UserChatInput):
    def __init__(
            self,
            string_input: ta.Callable[[], ta.Awaitable[str]] | None = None,
    ) -> None:
        super().__init__()

        if string_input is None:
            string_input = lang.as_async(functools.partial(input, '> '))
        self._string_input = string_input

    async def get_next_user_messages(self) -> mc.UserChat:
        try:
            s = await self._string_input()
        except EOFError:
            return []
        return [mc.UserMessage(s)]
