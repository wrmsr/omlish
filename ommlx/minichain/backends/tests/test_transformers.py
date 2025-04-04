import pytest

from omlish.testing import pytest as ptu

from ...prompts import PromptRequest
from ..transformers import TransformersPromptService


@pytest.mark.not_docker_guest
@ptu.skip.if_cant_import('transformers')
def test_transformers():
    llm = TransformersPromptService('Qwen/Qwen2-0.5B', dict(max_new_tokens=20, device=None))

    resp = llm.invoke(PromptRequest.new('Is water dry?'))
    print(resp)
    assert resp.text

    resp = llm('Is water dry?')
    print(resp)
    assert resp.text
