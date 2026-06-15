from omlish import check
from omlish import lang

from ..generations import ChatGeneration
from ..history import HistoryAddingChatService
from ..history import ListChatHistory
from ..messages import AiMessage
from ..messages import Chat
from ..messages import UserMessage
from ..services import ChatRequest
from .dummy import DummyChatService


def test_history_chat_service():
    def fn(c: Chat) -> ChatGeneration:
        return ChatGeneration([
            AiMessage(f'{len(c)}:{check.isinstance(check.isinstance(c[-1], UserMessage).c, str)}'),
        ])

    ch = ListChatHistory()
    svc = HistoryAddingChatService(DummyChatService(fn), ch)

    assert (am0 := check.single(lang.sync_await(svc.invoke(ChatRequest([um0 := UserMessage('hi')]))).v.chat)) == AiMessage('1:hi')  # noqa
    assert (am1 := check.single(lang.sync_await(svc.invoke(ChatRequest([um1 := UserMessage('again')]))).v.chat)) == AiMessage('3:again')  # noqa

    assert list(ch.get()) == [um0, am0, um1, am1]
