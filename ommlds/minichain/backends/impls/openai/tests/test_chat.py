import typing as ta

from omlish import check
from omlish import lang
from omlish import marshal as msh
from omlish.http import all as http
from omlish.secrets.tests.harness import HarnessSecrets

from .....chat.choices.services import ChatChoicesRequest
from .....chat.choices.services import ChatChoicesService
from .....chat.messages import Message
from .....chat.messages import SystemMessage
from .....chat.messages import ToolUseMessage
from .....chat.messages import ToolUseResultMessage
from .....chat.messages import UserMessage
from .....chat.tools.types import Tool
from .....content.text import TextContent
from .....llms.types import MaxCompletionTokens
from .....standard import ApiKey
from .....standard import DefaultOptions
from .....tools.types import ToolDtype
from .....tools.types import ToolParam
from .....tools.types import ToolSpec
from .....tools.types import ToolUseResult
from ..chat import OpenaiChatChoicesService


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


def test_openai_content(harness):
    llm = OpenaiChatChoicesService(
        ApiKey(harness[HarnessSecrets].get_or_skip('openai_api_key').reveal()),
        http_client=http.SyncAsyncHttpClient(http.client()),
    )

    req = ChatChoicesRequest(
        [UserMessage(['Is water ', [TextContent('dry?')]])],
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
            MaxCompletionTokens(64),
            Tool(tool_spec),
        ],
    )))

    print(resp)
    assert resp.v

    tum = check.isinstance(check.single(check.single(resp.v).ms), ToolUseMessage)
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


def test_openai_chat_promote(harness):
    llm: ChatChoicesService = ta.cast(ChatChoicesService, OpenaiChatChoicesService(
        ApiKey(harness[HarnessSecrets].get_or_skip('openai_api_key').reveal()),
        http_client=http.SyncAsyncHttpClient(http.client()),
    ))

    assert lang.sync_await(llm.invoke(ChatChoicesRequest([UserMessage('Hi!')]))).v
    assert lang.sync_await(llm.invoke(ChatChoicesRequest([UserMessage('Hi!')]))).v


def test_default_options(harness):
    llm: ChatChoicesService = ta.cast(ChatChoicesService, OpenaiChatChoicesService(
        ApiKey(harness[HarnessSecrets].get_or_skip('openai_api_key').reveal()),
        DefaultOptions([
            MaxCompletionTokens(100),
        ]),
        http_client=http.SyncAsyncHttpClient(http.client()),
    ))

    assert lang.sync_await(llm.invoke(ChatChoicesRequest([UserMessage('Hi!')]))).v
    assert lang.sync_await(llm.invoke(ChatChoicesRequest([UserMessage('Hi!')], [MaxCompletionTokens(101)]))).v
