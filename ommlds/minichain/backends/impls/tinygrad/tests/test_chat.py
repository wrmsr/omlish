import pytest

from omlish import lang

from .....chat.messages import UserMessage
from .....services import Request
from ..chat import TinygradLlama3ChatChoicesService


@pytest.mark.not_docker_guest
@pytest.mark.high_mem
def test_tinygrad():
    with TinygradLlama3ChatChoicesService() as llm:
        q = 'Is a bird a mammal?'

        resp = lang.sync_await(llm.invoke(Request([UserMessage(q)])))
        print(resp)
        assert resp.v
