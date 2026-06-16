from omlish import lang

from ....chat.choices.services import ChatChoicesRequest
from ....chat.messages import Message
from ....chat.messages import UserMessage
from ....chat.stream.choices.services import ChatChoicesStreamRequest
from ..chat import DummyChatChoicesService
from ..chat import DummyChatChoicesStreamService


def test_dummy_chat(harness):
    chat: list[Message] = [
        UserMessage('hi'),
    ]

    llm = DummyChatChoicesService()

    resp = lang.sync_await(llm.invoke(ChatChoicesRequest(
        chat,
    )))

    print(resp)


def test_dummy_chat_stream_model(harness):
    llm = DummyChatChoicesStreamService()

    foo_req = ChatChoicesStreamRequest([UserMessage('hi')])

    with lang.sync_async_with(lang.sync_await(llm.invoke(foo_req)).v) as it:
        for o in lang.sync_aiter(it):
            print(o)
        print(it.returned.must())
