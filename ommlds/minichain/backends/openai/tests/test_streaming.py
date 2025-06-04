from omlish.secrets.tests.harness import HarnessSecrets

from ....chat.messages import UserMessage
from ....chat.services import ChatRequest
from ....standard import ApiKey
from ..streaming import OpenaiChatStreamService


def test_openai_chat_streaming_model(harness):
    llm = OpenaiChatStreamService(
        ApiKey(harness[HarnessSecrets].get_or_skip('openai_api_key').reveal()),
    )

    foo_req: ChatRequest
    for foo_req in [
        ChatRequest([UserMessage('Is water dry?')]),
        ChatRequest([UserMessage('Is air wet?')]),
    ]:
        print(foo_req)

        with llm.invoke(foo_req).v as it:
            for o in it:
                print(o)
