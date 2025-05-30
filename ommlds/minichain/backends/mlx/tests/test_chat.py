import pytest

from ....chat.messages import UserMessage
from ....standard import ModelName
from ..chat import MlxChatService


@pytest.mark.not_docker_guest
@pytest.mark.high_mem
def test_mlx():
    with MlxChatService(ModelName('mlx-community/Qwen2.5-0.5B-4bit')) as llm:
        q = 'Is a bird a mammal?'

        resp = llm([UserMessage(q)])
        print(resp)
        assert resp.choices
