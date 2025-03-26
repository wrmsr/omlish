from omlish.testing import pytest as ptu

from ...chat.messages import UserMessage
from ...generative import MaxTokens
from ...generative import Temperature
from ..llamacpp import LlamacppChatModel
from ..llamacpp import LlamacppPromptModel


@ptu.skip.if_cant_import('llama_cpp')
def test_llamacpp_prompt():
    llm = LlamacppPromptModel()
    resp = llm(
        'Is water dry?',
        Temperature(.1),
        MaxTokens(64),
    )
    print(resp)
    assert resp.v


@ptu.skip.if_cant_import('llama_cpp')
def test_llamacpp_chat_model():
    llm = LlamacppChatModel()
    resp = llm(
        [UserMessage('Is water dry?')],
        Temperature(.1),
        MaxTokens(64),
    )
    print(resp)
    assert resp.v[0].m.s
