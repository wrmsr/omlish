import pytest

from omlish import lang
from omlish.secrets.tests.harness import HarnessSecrets

from .....chat.messages import UserMessage
from .....chat.stream.services import ChatChoicesStreamRequest
from .....standard import ApiKey
from ..stream import AnthropicChatChoicesStreamService


@pytest.mark.skip_unless_alone
def test_anthropic_chat_stream_model(harness):
    llm = AnthropicChatChoicesStreamService(
        ApiKey(harness[HarnessSecrets].get_or_skip('anthropic_api_key').reveal()),
    )

    foo_req: ChatChoicesStreamRequest
    for foo_req in [
        ChatChoicesStreamRequest([UserMessage('Is water dry?')]),
        ChatChoicesStreamRequest([UserMessage('Is air wet?')]),
    ]:
        print(foo_req)

        with lang.sync_await(llm.invoke(foo_req)).v as it:
            for o in it:
                print(o)
            print(it.outputs)
