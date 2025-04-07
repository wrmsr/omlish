from omlish.secrets.tests.harness import HarnessSecrets

from ....chat.messages import UserMessage
from ....chat.streaming import ChatStreamRequest
from ..streaming import OpenaiChatStreamService


def test_openai_chat_streaming_model(harness):
    llm = OpenaiChatStreamService(
        api_key=harness[HarnessSecrets].get_or_skip('openai_api_key').reveal(),
    )

    foo_req: ChatStreamRequest
    for foo_req in [
        ChatStreamRequest([UserMessage('Is water dry?')]),
        ChatStreamRequest([UserMessage('Is air wet?')]),
    ]:
        print(foo_req)

        with llm.invoke(foo_req) as foo_resp:
            print(foo_resp)
            for o in foo_resp:
                print(o)
