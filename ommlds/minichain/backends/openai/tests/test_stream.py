from omlish.secrets.tests.harness import HarnessSecrets

from ....chat.choices.adapters import ChatChoicesServiceChatService
from ....chat.messages import UserMessage
from ....chat.services import ChatService
from ....chat.stream.adapters import ChatChoicesStreamServiceChatChoicesService
from ....chat.stream.services import ChatChoicesStreamRequest
from ....services import Request
from ....standard import ApiKey
from ..stream import OpenaiChatChoicesStreamService


def test_openai_chat_stream_model(harness):
    llm = OpenaiChatChoicesStreamService(
        ApiKey(harness[HarnessSecrets].get_or_skip('openai_api_key').reveal()),
    )

    foo_req: ChatChoicesStreamRequest
    for foo_req in [
        ChatChoicesStreamRequest([UserMessage('Is water dry?')]),
        ChatChoicesStreamRequest([UserMessage('Is air wet?')]),
    ]:
        print(foo_req)

        with llm.invoke(foo_req).v as it:
            for o in it:
                print(o)
            print(it.outputs)


def test_adapters(harness):
    llm: ChatService = ChatChoicesServiceChatService(
        ChatChoicesStreamServiceChatChoicesService(
            OpenaiChatChoicesStreamService(
                ApiKey(harness[HarnessSecrets].get_or_skip('openai_api_key').reveal()),
            ),
        ),
    )

    foo_req: Request
    for foo_req in [
        Request([UserMessage('Is water dry?')]),
        Request([UserMessage('Is air wet?')]),
    ]:
        print(llm.invoke(foo_req))
