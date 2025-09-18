import pytest

from omlish import lang

from .....chat.messages import UserMessage
from .....chat.services import ChatRequest
from ..stream import LlamacppChatChoicesStreamService


@pytest.mark.not_docker_guest
@pytest.mark.high_mem
def test_llamacpp_chat_stream_model():
    with LlamacppChatChoicesStreamService() as foo_svc:
        foo_req: ChatRequest
        for foo_req in [
            ChatRequest([UserMessage('Is water dry?')]),
            ChatRequest([UserMessage('Is air wet?')]),
        ]:
            print(foo_req)

            with lang.sync_async_with(lang.sync_await(foo_svc.invoke(foo_req)).v) as it:
                for o in lang.sync_aiter(it):
                    print(o)
