import pytest

from omlish.testing import pytest as ptu

from ...backends.mlxlm import MlxlmChatModel
from ...chat import UserMessage


@pytest.mark.not_docker_guest
@ptu.skip.if_cant_import('mlx_lm')
def test_mlxlm():
    llm = MlxlmChatModel('mlx-community/Qwen2.5-0.5B-4bit')

    q = 'Is a bird a mammal?'

    resp = llm([UserMessage(q)])
    print(resp)
    assert resp.v
