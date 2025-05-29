import pytest

from omlish.testing import pytest as ptu

from ...backends.tinygrad import TinygradLlama3ChatService
from ...chat.messages import UserMessage


@pytest.mark.not_docker_guest
@pytest.mark.high_mem
@ptu.skip.if_cant_import('tinygrad')
def test_tinygrad():
    with TinygradLlama3ChatService() as llm:
        q = 'Is a bird a mammal?'

        resp = llm([UserMessage(q)])
        print(resp)
        assert resp.choices
