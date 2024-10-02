import os.path

import pytest

from omlish.testing import pytest as ptu

from ..backends.openai import OpenaiChatModel
from ..backends.transformers import TransformersPromptModel
from ..chat import UserMessage
from ..prompts import Prompt
from ..prompts import PromptRequest


@pytest.mark.not_docker_guest
@ptu.skip.if_cant_import('transformers')
def test_transformers():
    llm = TransformersPromptModel('Qwen/Qwen2-0.5B', dict(max_new_tokens=20, device=None))

    resp = llm.generate(PromptRequest.new(Prompt('Is water dry?')))
    print(resp)
    assert resp.v

    resp = llm.generate_new(Prompt('Is water dry?'))
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

    resp = llm.generate_new([UserMessage.of('Is water dry?')])
    print(resp)
    assert resp.v
