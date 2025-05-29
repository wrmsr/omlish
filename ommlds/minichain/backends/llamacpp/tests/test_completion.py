import pytest

from ....llms.services import MaxTokens
from ..completion import LlamacppCompletionService


@pytest.mark.not_docker_guest
@pytest.mark.high_mem
def test_llamacpp_completion():
    llm = LlamacppCompletionService()
    resp = llm(
        'Is water dry?',
        # Temperature(.1),
        MaxTokens(64),
    )
    print(resp)
    assert resp.text
