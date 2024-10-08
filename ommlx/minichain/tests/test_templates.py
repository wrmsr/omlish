import os.path
import typing as ta

import pytest

from ..backends.openai import OpenaiPromptModel
from ..generative import MaxTokens
from ..generative import Temperature
from ..prompts import Prompt
from ..prompts import PromptModel
from ..templates import DictTemplater
from ..templates import TemplatingModel


def test_templates():
    assert DictTemplater(dict(x='foo')).apply('hi {x}!') == 'hi foo!'


def test_templating_model():
    env_file = os.path.join(os.path.expanduser('~/.omlish-llm/.env'))
    if not os.path.isfile(env_file):
        pytest.skip('No env file')
    with open(env_file) as f:
        for l in f:
            if l := l.strip():
                k, _, v = l.partition('=')
                os.environ[k] = v

    llm: PromptModel = OpenaiPromptModel()
    llm = ta.cast(PromptModel, TemplatingModel(llm, DictTemplater(dict(what='water'))))

    resp = llm(
        Prompt('Is {what} dry?'),
        Temperature(.1),
        MaxTokens(64),
    )
    print(resp)
    assert resp.v
