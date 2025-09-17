from omlish import lang

from ..messages import UserMessage
from ..services import ChatRequest
from .dummy import DummyChatService


def test_dummy():
    assert lang.sync_await(DummyChatService.simple(lambda s: s + '!').invoke(ChatRequest([UserMessage('hi')]))).v.c == 'hi!'  # noqa
