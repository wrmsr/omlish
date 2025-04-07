from omlish.testing import pytest as ptu

from ..prompt import LlamacppPromptService


@ptu.skip.if_cant_import('llama_cpp')
def test_llamacpp_prompt():
    llm = LlamacppPromptService()
    resp = llm(
        'Is water dry?',
        # Temperature(.1),
        # MaxTokens(64),
    )
    print(resp)
    assert resp.text
