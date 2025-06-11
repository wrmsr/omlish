import pytest

from ....chat.messages import UserMessage
from ....services import Request
from ....standard import ModelName
from ..chat import MlxChatChoicesService


@pytest.mark.not_docker_guest
@pytest.mark.high_mem
def test_mlx():
    with MlxChatChoicesService(ModelName('mlx-community/Qwen2.5-0.5B-4bit')) as llm:
        q = 'Is a bird a mammal?'

        resp = llm.invoke(Request([UserMessage(q)]))
        print(resp)
        assert resp.v
