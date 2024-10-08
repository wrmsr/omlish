import os.path
import typing as ta

import pytest

from ..backends.openai import OpenaiPromptModel
from ..generative import MaxTokens
from ..generative import Temperature
from ..models import Model
from ..models import Option
from ..models import Request
from ..models import Response
from ..prompts import Prompt
from ..prompts import PromptModel


class WrapperModel(Model):
    def __init__(self, underlying: Model) -> None:
        super().__init__()
        self._underlying = underlying

    @property
    def request_cls(self) -> type[Request]:  # type: ignore[override]
        return self._underlying.request_cls

    @property
    def option_cls_set(self) -> frozenset[type[Option]]:  # type: ignore[override]
        return self._underlying.option_cls_set

    @property
    def response_cls(self) -> type[Response]:  # type: ignore[override]
        return self._underlying.response_cls

    def invoke(self, request: Request) -> Response:
        return self._underlying.invoke(request)


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
    llm = ta.cast(PromptModel, WrapperModel(llm))

    resp = llm(
        Prompt('Is water dry?'),
        Temperature(.1),
        MaxTokens(64),
    )
    print(resp)
    assert resp.v
