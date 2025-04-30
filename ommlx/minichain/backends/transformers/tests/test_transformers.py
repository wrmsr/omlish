import pytest

from omlish.testing import pytest as ptu

from ....completion import CompletionRequest
from ..transformers import TransformersCompletionService


@pytest.mark.not_docker_guest
@ptu.skip.if_cant_import('transformers')
def test_transformers():
    llm = TransformersCompletionService('Qwen/Qwen2-0.5B', dict(max_new_tokens=20, device=None))

    resp = llm.invoke(CompletionRequest.new('Is water dry?'))
    print(resp)
    assert resp.text

    resp = llm('Is water dry?')
    print(resp)
    assert resp.text
