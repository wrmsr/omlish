import typing as ta

from omlish import check
from omlish import marshal as msh
from omlish.secrets.tests.harness import HarnessSecrets

from ....chat.messages import Message
from ....chat.messages import SystemMessage
from ....chat.messages import ToolExecResultMessage
from ....chat.messages import UserMessage
from ....chat.services import ChatRequest
from ....chat.services import ChatService_
from ....chat.tools import Tool
from ....llms.services import MaxTokens
from ....llms.services import Temperature
from ....standard import ApiKey
from ....standard import DefaultRequestOptions
from ....tools import ToolParam
from ....tools import ToolSpec
from ..chat import OpenaiChatService


def test_openai(harness):
    llm = OpenaiChatService(ApiKey(harness[HarnessSecrets].get_or_skip('openai_api_key').reveal()))

    req: ChatRequest = ChatRequest.new(
        [UserMessage('Is water dry?')],
        Temperature(.1),
        MaxTokens(64),
    )

    rm = msh.marshal(req)
    print(rm)
    req2 = msh.unmarshal(rm, ChatRequest)
    print(req2)

    resp = llm(req)
    print(resp)
    assert resp.choices


def test_openai_tools(harness):
    llm = OpenaiChatService(ApiKey(harness[HarnessSecrets].get_or_skip('openai_api_key').reveal()))

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
    assert resp.choices

    chat.append(resp.choices[0].m)

    tr = check.single(check.not_none(resp.choices[0].m.tool_exec_requests))
    assert tr.spec.name == 'get_weather'
    assert tr.args == {'location': 'Seattle'}

    chat.append(ToolExecResultMessage(tr.id, tr.spec.name, '"rain"'))

    resp = llm(
        chat,
        Temperature(.1),
        MaxTokens(64),
        Tool(tool_spec),
    )

    print(resp)
    assert resp.choices


def test_openai_chat_promote(harness):
    llm: ChatService_ = ta.cast(ChatService_, OpenaiChatService(
        ApiKey(harness[HarnessSecrets].get_or_skip('openai_api_key').reveal()),
    ))

    assert llm([UserMessage('Hi!')]).choices
    assert llm(ChatRequest([UserMessage('Hi!')])).choices


def test_default_options(harness):
    llm: ChatService_ = ta.cast(ChatService_, OpenaiChatService(
        ApiKey(harness[HarnessSecrets].get_or_skip('openai_api_key').reveal()),
        DefaultRequestOptions([MaxTokens(100)]),
    ))

    assert llm([UserMessage('Hi!')]).choices
    assert llm([UserMessage('Hi!')], MaxTokens(101)).choices
