from omlish import check
from omlish import lang

from ..history import HistoryAddingChatService
from ..history import ListChatHistory
from ..messages import AiChat
from ..messages import AiMessage
from ..messages import Chat
from ..messages import UserMessage
from ..services import ChatRequest
from .dummy import DummyChatService


def test_history_chat_service():
    def fn(c: Chat) -> AiChat:
        return [AiMessage(f'{len(c)}:{check.isinstance(check.isinstance(c[-1], UserMessage).c, str)}')]

    ch = ListChatHistory()
    svc = HistoryAddingChatService(DummyChatService(fn), ch)

    assert (am0 := check.single(lang.sync_await(svc.invoke(ChatRequest([um0 := UserMessage('hi')]))).v)) == AiMessage('1:hi')  # noqa
    assert (am1 := check.single(lang.sync_await(svc.invoke(ChatRequest([um1 := UserMessage('again')]))).v)) == AiMessage('3:again')  # noqa

    assert list(ch.get()) == [um0, am0, um1, am1]
