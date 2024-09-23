from omlish.testing import pytest as ptu

from ..backends.transformers import TransformersPromptModel
from ..models import Request
from ..prompts import Prompt


@ptu.skip_if_cant_import('transformers')
def test_minichain():
    llm = TransformersPromptModel('Qwen/Qwen2-0.5B')
    resp = llm.generate(Request(Prompt('Is water dry?')))
    print(resp)
    assert resp.v
