import pytest

from ....chat.messages import UserMessage
from ....services import Request
from ..chat import LlamacppChatChoicesService


@pytest.mark.not_docker_guest
@pytest.mark.high_mem
def test_llamacpp_chat_model():
    llm = LlamacppChatChoicesService()
    resp = llm.invoke(Request(
        [UserMessage('Is water dry?')],
        # Temperature(.1),
        # MaxTokens(64),
    ))
    print(resp)
    assert resp.v[0].m.c
