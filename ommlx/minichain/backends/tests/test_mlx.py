import pytest

from omlish.testing import pytest as ptu

from ...backends.mlx import MlxChatService
from ...chat.messages import UserMessage


@pytest.mark.not_docker_guest
@ptu.skip.if_cant_import('mlx_lm')
def test_mlx():
    llm = MlxChatService('mlx-community/Qwen2.5-0.5B-4bit')

    q = 'Is a bird a mammal?'

    resp = llm([UserMessage(q)])
    print(resp)
    assert resp.choices
