import pytest

from omlish.testing import pytest as ptu

from ...backends.mlxlm import MlxlmChatModel
from ...chat import UserMessage


@pytest.mark.not_docker_guest
@ptu.skip.if_cant_import('mlx_lm')
def test_mlxlm():
    llm = MlxlmChatModel('mlx-community/mamba-2.8b-hf-f16')

    resp = llm([UserMessage('Is water dry?')])
    print(resp)
    assert resp.v

    resp = llm('Is water dry?')
    print(resp)
    assert resp.v
