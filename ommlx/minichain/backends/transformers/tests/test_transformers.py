import pytest

from omlish.testing import pytest as ptu

from ....completion import CompletionRequest
from ....standard import ModelPath
from ..transformers import TransformersCompletionService
from ..transformers import TransformersPipelineKwargs


@pytest.mark.not_docker_guest
@ptu.skip.if_cant_import('transformers')
def test_transformers():
    llm = TransformersCompletionService(
        ModelPath('Qwen/Qwen2-0.5B'),
        TransformersPipelineKwargs(dict(
            max_new_tokens=20,
            # device=None,
        )),
    )

    resp = llm.invoke(CompletionRequest.new('Is water dry?'))
    print(resp)
    assert resp.text

    resp = llm('Is water dry?')
    print(resp)
    assert resp.text
