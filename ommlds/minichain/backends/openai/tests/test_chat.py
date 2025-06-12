import typing as ta

from omlish import check
from omlish import marshal as msh
from omlish.secrets.tests.harness import HarnessSecrets

from ....chat.choices.services import ChatChoicesRequest
from ....chat.choices.services import ChatChoicesService
from ....chat.messages import Message
from ....chat.messages import SystemMessage
from ....chat.messages import ToolExecResultMessage
from ....chat.messages import UserMessage
from ....chat.tools import Tool
from ....llms.services import MaxTokens
from ....llms.services import Temperature
from ....standard import ApiKey
from ....standard import DefaultOptions
from ....tools.types import ToolDtype
from ....tools.types import ToolParam
from ....tools.types import ToolSpec
from ..chat import OpenaiChatChoicesService


def test_openai(harness):
    llm = OpenaiChatChoicesService(ApiKey(harness[HarnessSecrets].get_or_skip('openai_api_key').reveal()))

    req = ChatChoicesRequest(
        [UserMessage('Is water dry?')],
        [
            Temperature(.1),
            MaxTokens(64),
        ],
    )

    rm = msh.marshal(req)
    print(rm)
    req2 = msh.unmarshal(rm, ChatChoicesRequest)
    print(req2)

    resp = llm.invoke(req)
    print(resp)
    assert resp.v


def test_openai_tools(harness):
    llm = OpenaiChatChoicesService(ApiKey(harness[HarnessSecrets].get_or_skip('openai_api_key').reveal()))

    tool_spec = ToolSpec(
        'get_weather',
        params=[
            ToolParam(
                'location',
                type=ToolDtype.of(str),
                desc='The location to get the weather for.',
            ),
        ],
        desc='Gets the weather in the given location.',
    )

    chat: list[Message] = [
        SystemMessage("You are a helpful agent. Use any tools available to you to answer the user's questions."),
        UserMessage('What is the weather in Seattle?'),
    ]

    resp = llm.invoke(ChatChoicesRequest(
        chat,
        [
            Temperature(.1),
            MaxTokens(64),
            Tool(tool_spec),
        ],
    ))

    print(resp)
    assert resp.v

    chat.append(resp.v[0].m)

    tr = check.single(check.not_none(resp.v[0].m.tool_exec_requests))
    assert tr.spec.name == 'get_weather'
    assert tr.args == {'location': 'Seattle'}

    chat.append(ToolExecResultMessage(tr.id, tr.spec.name, '"rain"'))

    resp = llm.invoke(ChatChoicesRequest(
        chat,
        [
            Temperature(.1),
            MaxTokens(64),
            Tool(tool_spec),
        ],
    ))

    print(resp)
    assert resp.v


def test_openai_chat_promote(harness):
    llm: ChatChoicesService = ta.cast(ChatChoicesService, OpenaiChatChoicesService(
        ApiKey(harness[HarnessSecrets].get_or_skip('openai_api_key').reveal()),
    ))

    assert llm.invoke(ChatChoicesRequest([UserMessage('Hi!')])).v
    assert llm.invoke(ChatChoicesRequest([UserMessage('Hi!')])).v


def test_default_options(harness):
    llm: ChatChoicesService = ta.cast(ChatChoicesService, OpenaiChatChoicesService(
        ApiKey(harness[HarnessSecrets].get_or_skip('openai_api_key').reveal()),
        DefaultOptions([MaxTokens(100)]),
    ))

    assert llm.invoke(ChatChoicesRequest([UserMessage('Hi!')])).v
    assert llm.invoke(ChatChoicesRequest([UserMessage('Hi!')], [MaxTokens(101)])).v
