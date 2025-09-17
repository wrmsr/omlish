from omlish import check
from omlish import lang

from ..history import HistoryAddingChatService
from ..history import ListChatHistory
from ..messages import AiMessage
from ..messages import Chat
from ..messages import UserMessage
from ..services import ChatRequest
from .dummy import DummyChatService


def test_history_chat_service():
    def fn(c: Chat) -> AiMessage:
        return AiMessage(f'{len(c)}:{check.isinstance(check.isinstance(c[-1], UserMessage).c, str)}')

    ch = ListChatHistory()
    svc = HistoryAddingChatService(DummyChatService(fn), ch)

    assert (am0 := lang.sync_await(svc.invoke(ChatRequest([um0 := UserMessage('hi')]))).v).c == '1:hi'
    assert (am1 := lang.sync_await(svc.invoke(ChatRequest([um1 := UserMessage('again')]))).v).c == '3:again'

    assert list(ch.get()) == [um0, am0, um1, am1]
