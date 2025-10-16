from ...... import minichain as mc
from .types import UserChatInput


##


class OneshotUserChatInput(UserChatInput):
    def __init__(
            self,
            initial_chat: mc.UserChat | None = None,
    ) -> None:
        super().__init__()

        self._pending_chat: mc.UserChat | None = initial_chat

    async def get_next_user_messages(self) -> mc.UserChat:
        ret = self._pending_chat
        self._pending_chat = None
        return ret or []
