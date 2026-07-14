import typing as ta

import pytest

from omlish import check
from omlish import lang
from omlish import marshal as msh
from omlish.http import all as http
from omlish.secrets.tests.harness import HarnessSecrets

from .....backends.openai import protocol as pt
from ....chat.choices.services import ChatChoicesRequest
from ....chat.choices.services import ChatChoicesService
from ....chat.messages import Message
from ....chat.messages import SystemMessage
from ....chat.messages import ToolUseMessage
from ....chat.messages import ToolUseResultMessage
from ....chat.messages import UserMessage
from ....chat.tools.types import Tool
from ....content.text import TextContent
from ....llms.types import MaxCompletionTokens
from ....standard import ApiKey
from ....tools.types import ToolDtype
from ....tools.types import ToolParam
from ....tools.types import ToolSpec
from ....tools.types import ToolUse
from ....tools.types import ToolUseResult
from ....wrappers.updateoptions import UpdateOptionsService
from ..chat import OpenaiChatChoicesService
from ..protocol import OpenaiChatRequestHandler
from ..protocol import build_oai_request_msgs


def test_openai_parallel_tool_call_request_messages():
    chat: list[Message] = [
        UserMessage('Use both tools.'),
        ToolUseMessage(ToolUse(
            id='call_1',
            name='first_tool',
            args={'value': 1},
            raw_args='{"value":1}',
        )),
        ToolUseMessage(ToolUse(
            id='call_2',
            name='second_tool',
            args={'value': 2},
            raw_args='{"value":2}',
        )),
        ToolUseResultMessage(ToolUseResult(
            id='call_1',
            name='first_tool',
            c='first result',
        )),
        ToolUseResultMessage(ToolUseResult(
            id='call_2',
            name='second_tool',
            c='second result',
        )),
    ]

    oai_msgs = list(build_oai_request_msgs(chat))

    assert len(oai_msgs) == 4
    assistant_msg = check.isinstance(oai_msgs[1], pt.AssistantChatCompletionMessage)
    assert assistant_msg.content is None
    tool_calls = list(check.not_none(assistant_msg.tool_calls))
    assert [tc.id for tc in tool_calls] == ['call_1', 'call_2']
    assert [tc.function.name for tc in tool_calls] == ['first_tool', 'second_tool']
    assert [tc.function.arguments for tc in tool_calls] == ['{"value":1}', '{"value":2}']

    tool_result_msgs = [
        check.isinstance(oai_msg, pt.ToolChatCompletionMessage)
        for oai_msg in oai_msgs[2:]
    ]
    assert [m.tool_call_id for m in tool_result_msgs] == ['call_1', 'call_2']


def test_openai_parallel_tool_calls_enabled_with_tools():
    tool_spec = ToolSpec(
        'get_weather',
        params=[
            ToolParam(
                'location',
                type=ToolDtype.of(str),
            ),
        ],
    )

    req = OpenaiChatRequestHandler(
        [UserMessage('What is the weather in Seattle?')],
        Tool(tool_spec),
        model='gpt-test',
    ).oai_request()

    assert req.tools is not None
    assert req.parallel_tool_calls is True


def test_openai_parallel_tool_calls_omitted_without_tools():
    req = OpenaiChatRequestHandler(
        [UserMessage('Hi!')],
        model='gpt-test',
    ).oai_request()

    assert req.tools is None
    assert req.parallel_tool_calls is None


@pytest.mark.online
@pytest.mark.asyncs('asyncio')
async def test_openai_async(harness):
    llm = OpenaiChatChoicesService(
        ApiKey(harness[HarnessSecrets].get_or_skip('openai_api_key').reveal()),
    )

    req = ChatChoicesRequest(
        [UserMessage('Is water dry?')],
        [
            # Temperature(.1),
            MaxCompletionTokens(64),
        ],
    )

    rm = msh.marshal(req)
    print(rm)
    req2 = msh.unmarshal(rm, ChatChoicesRequest)
    print(req2)

    resp = await llm.invoke(req)
    print(resp)
    assert resp.v


@pytest.mark.online
def test_openai(harness):
    llm = OpenaiChatChoicesService(
        ApiKey(harness[HarnessSecrets].get_or_skip('openai_api_key').reveal()),
        http_client=http.SyncAsyncHttpClient(http.client()),
    )

    req = ChatChoicesRequest(
        [UserMessage('Is water dry?')],
        [
            # Temperature(.1),
            MaxCompletionTokens(64),
        ],
    )

    rm = msh.marshal(req)
    print(rm)
    req2 = msh.unmarshal(rm, ChatChoicesRequest)
    print(req2)

    resp = lang.sync_await(llm.invoke(req))
    print(resp)
    assert resp.v


@pytest.mark.online
def test_openai_content(harness):
    llm = OpenaiChatChoicesService(
        ApiKey(harness[HarnessSecrets].get_or_skip('openai_api_key').reveal()),
        http_client=http.SyncAsyncHttpClient(http.client()),
    )

    req = ChatChoicesRequest(
        [UserMessage(TextContent('Is water dry?'))],
        [
            # Temperature(.1),
            MaxCompletionTokens(64),
        ],
    )

    rm = msh.marshal(req)
    print(rm)
    req2 = msh.unmarshal(rm, ChatChoicesRequest)
    print(req2)

    resp = lang.sync_await(llm.invoke(req))
    print(resp)
    assert resp.v


@pytest.mark.online
def test_openai_tools(harness):
    llm = OpenaiChatChoicesService(
        ApiKey(harness[HarnessSecrets].get_or_skip('openai_api_key').reveal()),
        http_client=http.SyncAsyncHttpClient(http.client()),
    )

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

    resp = lang.sync_await(llm.invoke(ChatChoicesRequest(
        chat,
        [
            # Temperature(.1),
            MaxCompletionTokens(1024),
            Tool(tool_spec),
        ],
    )))

    print(resp)
    assert resp.v

    tum = check.isinstance(check.single(check.single(resp.v.gs).chat), ToolUseMessage)
    chat.append(tum)

    tr = tum.tu
    assert tr.name == 'get_weather'
    assert tr.args == {'location': 'Seattle'}

    chat.append(ToolUseResultMessage(ToolUseResult(
        id=tr.id,
        name=tr.name,
        c='"rain"',
    )))

    resp = lang.sync_await(llm.invoke(ChatChoicesRequest(
        chat,
        [
            # Temperature(.1),
            MaxCompletionTokens(64),
            Tool(tool_spec),
        ],
    )))

    print(resp)
    assert resp.v


@pytest.mark.online
def test_openai_chat_promote(harness):
    llm: ChatChoicesService = ta.cast(ChatChoicesService, OpenaiChatChoicesService(
        ApiKey(harness[HarnessSecrets].get_or_skip('openai_api_key').reveal()),
        http_client=http.SyncAsyncHttpClient(http.client()),
    ))

    assert lang.sync_await(llm.invoke(ChatChoicesRequest([UserMessage('Hi!')]))).v
    assert lang.sync_await(llm.invoke(ChatChoicesRequest([UserMessage('Hi!')]))).v


@pytest.mark.online
def test_add_options(harness):
    llm: ta.Any = UpdateOptionsService(
        OpenaiChatChoicesService(
            ApiKey(harness[HarnessSecrets].get_or_skip('openai_api_key').reveal()),  # noqa
            http_client=http.SyncAsyncHttpClient(http.client()),
        ),
        MaxCompletionTokens(100),
        mode='default',
    )

    assert lang.sync_await(llm.invoke(ChatChoicesRequest([UserMessage('Hi!')]))).v
    assert lang.sync_await(llm.invoke(ChatChoicesRequest([UserMessage('Hi!')], [MaxCompletionTokens(101)]))).v
