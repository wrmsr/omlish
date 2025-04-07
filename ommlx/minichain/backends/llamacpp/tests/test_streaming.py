from omlish.testing import pytest as ptu

from ....chat.messages import UserMessage
from ....chat.streaming import ChatStreamRequest
from ..streaming import LlamacppChatStreamService


@ptu.skip.if_cant_import('llama_cpp')
def test_llamacpp_chat_streaming_model():
    with LlamacppChatStreamService() as foo_svc:
        foo_req: ChatStreamRequest
        for foo_req in [
            ChatStreamRequest([UserMessage('Is water dry?')]),
            ChatStreamRequest([UserMessage('Is air wet?')]),
        ]:
            print(foo_req)

            with foo_svc.invoke(foo_req) as foo_resp:
                print(foo_resp)
                for o in foo_resp:
                    print(o)
