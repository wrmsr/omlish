import pytest

from omlish.secrets.tests.harness import HarnessSecrets
from omlish.testing import pytest as ptu

from ..backends.llamacpp import LlamacppPromptModel
from ..backends.openai import OpenaiChatModel
from ..backends.transformers import TransformersPromptModel
from ..generative import MaxTokens
from ..generative import Temperature
from ..prompts import Prompt
from ..prompts import PromptRequest


@pytest.mark.not_docker_guest
@ptu.skip.if_cant_import('transformers')
def test_transformers():
    llm = TransformersPromptModel('Qwen/Qwen2-0.5B', dict(max_new_tokens=20, device=None))

    resp = llm.invoke(PromptRequest.new(Prompt('Is water dry?')))
    print(resp)
    assert resp.v

    resp = llm(Prompt('Is water dry?'))
    print(resp)
    assert resp.v


def test_openai(harness):
    llm = OpenaiChatModel(api_key=harness[HarnessSecrets].get_or_skip('openai_api_key').reveal())

    resp = llm(
        'Is water dry?',
        Temperature(.1),
        MaxTokens(64),
    )
    print(resp)
    assert resp.v


@ptu.skip.if_cant_import('llama_cpp')
def test_llamacpp():
    llm = LlamacppPromptModel()
    resp = llm(
        Prompt('Is water dry?'),
        Temperature(.1),
        MaxTokens(64),
    )
    print(resp)
    assert resp.v
