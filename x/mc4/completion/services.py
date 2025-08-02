import typing as ta

from omlish import dataclasses as dc
from ommlds import minichain as mc

from .base import ChatCompleter


##


@dc.dataclass(frozen=True)
class ChatServiceChatCompleter(ChatCompleter):
    service: mc.ChatService

    @ta.override
    def complete_chat(self, chat: mc.Chat) -> mc.Chat:
        response = self.service.invoke(mc.ChatRequest(chat))
        return [response.v]
