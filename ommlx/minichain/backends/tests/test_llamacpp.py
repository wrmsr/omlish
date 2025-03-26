from omlish.testing import pytest as ptu

from ...generative import MaxTokens
from ...generative import Temperature
from ..llamacpp import LlamacppPromptModel


@ptu.skip.if_cant_import('llama_cpp')
def test_llamacpp():
    llm = LlamacppPromptModel()
    resp = llm(
        'Is water dry?',
        Temperature(.1),
        MaxTokens(64),
    )
    print(resp)
    assert resp.v
