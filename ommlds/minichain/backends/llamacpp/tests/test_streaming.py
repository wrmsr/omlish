import pytest

from ....chat.messages import UserMessage
from ....chat.services import ChatRequest
from ..streaming import LlamacppChatChoicesStreamService


@pytest.mark.not_docker_guest
@pytest.mark.high_mem
def test_llamacpp_chat_streaming_model():
    with LlamacppChatChoicesStreamService() as foo_svc:
        foo_req: ChatRequest
        for foo_req in [
            ChatRequest([UserMessage('Is water dry?')]),
            ChatRequest([UserMessage('Is air wet?')]),
        ]:
            print(foo_req)

            with foo_svc.invoke(foo_req).v as it:
                for o in it:
                    print(o)
