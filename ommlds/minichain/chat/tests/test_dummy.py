from omlish import check
from omlish import lang

from ..messages import AiMessage
from ..messages import UserMessage
from ..services import ChatRequest
from .dummy import DummyChatService


def test_dummy():
    resp = lang.sync_await(DummyChatService.simple(lambda s: s + '!').invoke(ChatRequest([UserMessage('hi')])))
    assert check.isinstance(check.single(resp.v), AiMessage).c == 'hi!'  # noqa
