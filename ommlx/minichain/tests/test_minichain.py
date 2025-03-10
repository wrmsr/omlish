import pytest

from omlish import check
from omlish.formats import json
from omlish.secrets.tests.harness import HarnessSecrets
from omlish.testing import pytest as ptu

from ..backends.llamacpp import LlamacppPromptModel
from ..backends.openai import OpenaiChatModel
from ..backends.transformers import TransformersPromptModel
from ..chat.messages import Message
from ..chat.messages import SystemMessage
from ..chat.messages import ToolExecResultMessage
from ..chat.messages import UserMessage
from ..chat.tools import Tool
from ..chat.tools import ToolParam
from ..chat.tools import ToolSpec
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

    chat: list[Message] = [
        SystemMessage("You are a helpful agent. Use any tools available to you to answer the user's questions."),
        UserMessage('What is the weather in Seattle?'),
    ]

    resp = llm(
        chat,
        Temperature(.1),
        MaxTokens(64),
        Tool(tool_spec),
    )

    print(resp)
    assert resp.v

    chat.append(resp.v[0].m)

    tr = check.single(check.not_none(resp.v[0].m.tool_exec_requests))
    assert tr.spec.name == 'get_weather'
    assert json.loads(tr.args) == {'location': 'Seattle'}

    chat.append(ToolExecResultMessage(tr.id, tr.spec.name, '"rain"'))

    resp = llm(
        chat,
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
