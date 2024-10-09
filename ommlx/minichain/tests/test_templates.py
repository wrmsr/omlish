import typing as ta

from omlish.secrets.tests.harness import HarnessSecrets
from omlish.testing import pytest as ptu

from ..backends.openai import OpenaiPromptModel
from ..generative import MaxTokens
from ..generative import Temperature
from ..prompts import PromptModel
from ..templates import DictTemplater
from ..templates import TemplatingModel


def test_templates():
    assert DictTemplater(dict(x='foo')).apply('hi {x}!') == 'hi foo!'


@ptu.skip.if_cant_import('openai')
def test_templating_model(harness):
    llm: PromptModel = OpenaiPromptModel(api_key=harness[HarnessSecrets].get_or_skip('openai_api_key').reveal())
    llm = ta.cast(PromptModel, TemplatingModel(llm, DictTemplater(dict(what='water'))))

    resp = llm(
        'Is {what} dry?',
        Temperature(.1),
        MaxTokens(64),
    )
    print(resp)
    assert resp.v
