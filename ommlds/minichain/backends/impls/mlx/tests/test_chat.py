import pytest

from omlish import lang

from .....chat.messages import UserMessage
from .....models.configs import ModelRepo
from .....services import Request
from ..chat import MlxChatChoicesService


@pytest.mark.not_docker_guest
@pytest.mark.high_mem
def test_mlx():
    with MlxChatChoicesService(ModelRepo('mlx-community', 'Qwen2.5-0.5B-4bit')) as llm:
        q = 'Is a bird a mammal?'

        resp = lang.sync_await(llm.invoke(Request([UserMessage(q)])))
        print(resp)
        assert resp.v
