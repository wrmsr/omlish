import pytest

from ....chat.messages import UserMessage
from ....services import Request
from ..chat import TinygradLlama3ChatService


@pytest.mark.not_docker_guest
@pytest.mark.high_mem
def test_tinygrad():
    with TinygradLlama3ChatService() as llm:
        q = 'Is a bird a mammal?'

        resp = llm.invoke(Request([UserMessage(q)]))
        print(resp)
        assert resp.v
