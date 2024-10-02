import pytest

from omlish.testing import pytest as ptu

from ..backends.transformers import TransformersPromptModel
from ..prompts import Prompt
from ..prompts import PromptRequest


@pytest.mark.not_docker_guest
@ptu.skip.if_cant_import('transformers')
def test_minichain():
    llm = TransformersPromptModel('Qwen/Qwen2-0.5B', dict(max_new_tokens=20, device=None))
    resp = llm.generate(PromptRequest.new(Prompt('Is water dry?')))
    print(resp)
    assert resp.v
