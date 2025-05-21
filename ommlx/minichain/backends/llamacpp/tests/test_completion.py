from omlish.testing import pytest as ptu

from ....llms.services import MaxTokens
from ..completion import LlamacppCompletionService


@ptu.skip.if_cant_import('llama_cpp')
def test_llamacpp_completion():
    llm = LlamacppCompletionService()
    resp = llm(
        'Is water dry?',
        # Temperature(.1),
        MaxTokens(64),
    )
    print(resp)
    assert resp.text
