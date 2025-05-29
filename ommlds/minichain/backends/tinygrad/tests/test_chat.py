import pytest

from ....chat.messages import UserMessage
from ..chat import TinygradLlama3ChatService


@pytest.mark.not_docker_guest
@pytest.mark.high_mem
def test_tinygrad():
    with TinygradLlama3ChatService() as llm:
        q = 'Is a bird a mammal?'

        resp = llm([UserMessage(q)])
        print(resp)
        assert resp.choices
