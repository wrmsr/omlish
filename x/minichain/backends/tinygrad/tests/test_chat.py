import pytest

from omlish import lang

from ....chat.messages import UserMessage
from ....services import Request
from ..chat import TinygradLlama3ChatChoicesService
from ..chat import TinygradLlama3ChatChoicesStreamService


@pytest.mark.not_docker_guest
@pytest.mark.high_mem
def test_tinygrad():
    with TinygradLlama3ChatChoicesService() as llm:
        q = 'Is a bird a mammal?'

        resp = lang.sync_await(llm.invoke(Request([UserMessage(q)])))
        print(resp)
        assert resp.v


@pytest.mark.not_docker_guest
@pytest.mark.high_mem
def test_tinygrad_stream():
    with TinygradLlama3ChatChoicesStreamService() as llm:
        q = 'Is a bird a mammal?'

        with lang.sync_async_with(lang.sync_await(llm.invoke(Request([UserMessage(q)]))).v) as it:
            for o in lang.sync_aiter(it):
                print(o)
        print(it.result.must())
