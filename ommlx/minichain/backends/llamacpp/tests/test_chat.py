from omlish.testing import pytest as ptu

from ....chat.messages import UserMessage
from ..chat import LlamacppChatService


@ptu.skip.if_cant_import('llama_cpp')
def test_llamacpp_chat_model():
    llm = LlamacppChatService()
    resp = llm(
        [UserMessage('Is water dry?')],
        # Temperature(.1),
        # MaxTokens(64),
    )
    print(resp)
    assert resp.choices[0].m.s
