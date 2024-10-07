import os.path

import pytest

from omlish.testing import pytest as ptu

from ..backends.llamacpp import LlamacppPromptModel
from ..backends.openai import OpenaiChatModel
from ..backends.transformers import TransformersPromptModel
from ..chat import UserMessage
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


def test_openai():
    env_file = os.path.join(os.path.expanduser('~/.omlish-llm/.env'))
    if not os.path.isfile(env_file):
        pytest.skip('No env file')
    with open(env_file) as f:
        for l in f:
            if l := l.strip():
                k, _, v = l.partition('=')
                os.environ[k] = v

    llm = OpenaiChatModel()

    resp = llm(
        [UserMessage.of('Is water dry?')],
        Temperature(.1),
        MaxTokens(64),
    )
    print(resp)
    assert resp.v


def test_llamacpp():
    llm = LlamacppPromptModel()
    resp = llm(
        Prompt('Is water dry?'),
        Temperature(.1),
        MaxTokens(64),
    )
    print(resp)
    assert resp.v
