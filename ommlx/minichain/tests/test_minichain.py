import pytest

from omlish.testing import pytest as ptu

from ..backends.transformers import TransformersPromptModel
from ..models import Request
from ..prompts import Prompt


@pytest.mark.not_docker_guest
@ptu.skip_if_cant_import('transformers')
def test_minichain():
    llm = TransformersPromptModel('Qwen/Qwen2-0.5B', dict(max_new_tokens=20, device=None))
    resp = llm.generate(Request(Prompt('Is water dry?')))
    print(resp)
    assert resp.v
