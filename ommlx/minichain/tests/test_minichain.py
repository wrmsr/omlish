import pytest

from omlish.secrets.tests.harness import HarnessSecrets
from omlish.testing import pytest as ptu

from ..backends.llamacpp import LlamacppPromptModel
from ..backends.openai import OpenaiChatModel
from ..backends.transformers import TransformersPromptModel
from ..chat import SystemMessage
from ..chat import Tool
from ..chat import ToolParam
from ..chat import ToolSpec
from ..chat import UserMessage
from ..generative import MaxTokens
from ..generative import Temperature
from ..prompts import PromptRequest


@pytest.mark.not_docker_guest
@ptu.skip.if_cant_import('transformers')
def test_transformers():
    llm = TransformersPromptModel('Qwen/Qwen2-0.5B', dict(max_new_tokens=20, device=None))

    resp = llm.invoke(PromptRequest.new('Is water dry?'))
    print(resp)
    assert resp.v

    resp = llm('Is water dry?')
    print(resp)
    assert resp.v


@ptu.skip.if_cant_import('openai')
def test_openai(harness):
    llm = OpenaiChatModel(api_key=harness[HarnessSecrets].get_or_skip('openai_api_key').reveal())

    resp = llm(
        [UserMessage('Is water dry?')],
        Temperature(.1),
        MaxTokens(64),
    )
    print(resp)
    assert resp.v


@ptu.skip.if_cant_import('openai')
def test_openai_tools(harness):
    llm = OpenaiChatModel(api_key=harness[HarnessSecrets].get_or_skip('openai_api_key').reveal())

    tool_spec = ToolSpec(
        'get_weather',
        [
            ToolParam('location', 'string', desc='The location to get the weather for.'),
        ],
        desc='Gets the weather in the given location.',
    )

    resp = llm(
        [
            SystemMessage("You are a helpful agent. Use any tools available to you to answer the user's questions."),
            UserMessage('What is the weather in Seattle?'),
        ],
        Temperature(.1),
        MaxTokens(64),
        Tool(tool_spec),
    )

    print(resp)
    assert resp.v


@ptu.skip.if_cant_import('llama_cpp')
def test_llamacpp():
    llm = LlamacppPromptModel()
    resp = llm(
        'Is water dry?',
        Temperature(.1),
        MaxTokens(64),
    )
    print(resp)
    assert resp.v
