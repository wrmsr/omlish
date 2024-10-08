import os.path
import typing as ta

import pytest

from ..backends.openai import OpenaiPromptModel
from ..generative import MaxTokens
from ..generative import Temperature
from ..models import Model
from ..models import Request
from ..models import Response
from ..prompts import Prompt
from ..prompts import PromptModel
from ..strings import transform_strings
from ..templates import DictTemplater
from ..templates import Templater
from ..wrappers import WrapperModel


class TemplatingModel(WrapperModel):
    def __init__(self, underlying: Model, templater: Templater) -> None:
        super().__init__(underlying)
        self._templater = templater

    def invoke(self, request: Request) -> Response:
        out_request = transform_strings(self._templater.apply, request)
        return super().invoke(out_request)


def test_openai_prompt():
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
