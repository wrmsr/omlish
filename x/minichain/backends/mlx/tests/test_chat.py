import pytest

from omlish import lang

from ....chat.messages import UserMessage
from ....models.configs import ModelRepo
from ....services import Request
from ..chat import MlxChatChoicesService
from ..chat import MlxChatChoicesStreamService


@pytest.mark.not_docker_guest
@pytest.mark.high_mem
def test_mlx():
    with MlxChatChoicesService(ModelRepo('mlx-community', 'Qwen2.5-0.5B-4bit')) as llm:
        q = 'Is a bird a mammal?'

        resp = lang.sync_await(llm.invoke(Request([UserMessage(q)])))
        print(resp)
        assert resp.v


@pytest.mark.not_docker_guest
@pytest.mark.high_mem
def test_mlx_stream():
    with MlxChatChoicesStreamService(ModelRepo('mlx-community', 'Qwen2.5-0.5B-4bit')) as llm:
        q = 'Is a bird a mammal?'

        with lang.sync_async_with(lang.sync_await(llm.invoke(Request([UserMessage(q)]))).v) as it:
            for o in lang.sync_aiter(it):
                print(o)
        print(it.result.must())
