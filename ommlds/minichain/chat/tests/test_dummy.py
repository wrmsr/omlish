from ..messages import UserMessage
from ..services import ChatRequest
from .dummy import DummyChatService


def test_dummy():
    assert DummyChatService.simple(lambda s: s + '!').invoke(ChatRequest([UserMessage('hi')])).v.s == 'hi!'
