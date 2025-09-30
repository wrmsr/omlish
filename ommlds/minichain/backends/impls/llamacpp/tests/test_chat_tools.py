import os.path

import pytest

from omlish import check
from omlish import lang

from .....chat.choices.adapters import ChatChoicesServiceChatService
from .....chat.messages import AiMessage
from .....chat.messages import ToolUseResultMessage
from .....chat.messages import UserMessage
from .....chat.services import ChatService
from .....chat.tools.ids import ToolUseIdAddingMessageTransform
from .....chat.messages import ToolUseMessage
from .....chat.tools.parsing import ToolExecParsingMessageTransform
from .....chat.tools.types import Tool
from .....chat.transforms.base import CompositeMessageTransform
from .....chat.transforms.base import MessageTransformChatTransform
from .....chat.transforms.metadata import CreatedAtAddingMessageTransform
from .....chat.transforms.metadata import UuidAddingMessageTransform
from .....chat.transforms.services import ResponseChatTransformingChatService
from .....models.configs import ModelPath
from .....services import Request
from .....text.toolparsing.dumb import DumbToolExecParser
from .....tools.types import ToolDtype
from .....tools.types import ToolParam
from .....tools.types import ToolSpec
from .....tools.types import ToolUseResult
from ..chat import LlamacppChatChoicesService


MODEL_PATHS = [
    os.path.expanduser(
        '~/Library/Caches/llama.cpp/bartowski_Qwen2.5-7B-Instruct-GGUF_Qwen2.5-7B-Instruct-Q4_K_M.gguf',
    ),
    os.path.expanduser(
        '~/.cache/huggingface/hub/models--Qwen--Qwen3-4B-GGUF/snapshots/'
        'bc640142c66e1fdd12af0bd68f40445458f3869b/Qwen3-4B-Q8_0.gguf',
    ),
]


@pytest.mark.not_docker_guest
@pytest.mark.high_mem
@pytest.mark.parametrize('model_path', MODEL_PATHS)
def test_llamacpp_chat_model_tools_qwen_raw(model_path):
    if not os.path.isfile(model_path):
        pytest.skip(f'No model: {model_path}')

    llm = LlamacppChatChoicesService(
        ModelPath(model_path),
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

    resp = lang.sync_await(llm.invoke(Request(
        [UserMessage('What is the weather in Seattle?')],
        [
            # Temperature(.1),
            # MaxTokens(64),
            Tool(tool_spec),
        ],
    )))

    print(resp)
    assert resp.v[0].m


@pytest.mark.not_docker_guest
@pytest.mark.high_mem
@pytest.mark.parametrize('model_path', MODEL_PATHS)
def test_llamacpp_chat_model_tools_qwen_parsed(model_path):
    if not os.path.isfile(model_path):
        pytest.skip(f'No model: {model_path}')

    llm: ChatService = ChatChoicesServiceChatService(
        LlamacppChatChoicesService(
            ModelPath(model_path),
        ),
    )

    llm = ResponseChatTransformingChatService(
        MessageTransformChatTransform(
            CompositeMessageTransform([
                CreatedAtAddingMessageTransform(),
                UuidAddingMessageTransform(),
                ToolExecParsingMessageTransform(
                    DumbToolExecParser(
                        '<tool_call>',
                        '</tool_call>',
                        strip_whitespace=True,
                    ),
                ),
                ToolUseIdAddingMessageTransform(),
            ]),
        ),
        llm,
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

    chat: list = [
        UserMessage('What is the weather in Seattle?'),
    ]

    resp = lang.sync_await(llm.invoke(Request(
        chat,
        [Tool(tool_spec)],
    )))

    print(resp)
    assert resp.v

    tum = check.isinstance(resp.v[-1], ToolUseMessage)
    chat.append(tum)

    tem = ToolUseResultMessage(ToolUseResult(
        id=tum.tu.id,
        name=tum.tu.name,
        c='"The weather in Seattle is rainy."',
    ))
    chat.append(tem)

    resp = lang.sync_await(llm.invoke(Request(
        chat,
        [Tool(tool_spec)],
    )))
    print(resp)


# @pytest.mark.not_docker_guest
# @pytest.mark.high_mem
# def test_llamacpp_chat_model_tools_watt():
#     model_path = os.path.join(
#         os.path.expanduser('~/.cache/huggingface/hub'),
#         'models--mradermacher--watt-tool-70B-GGUF/snapshots/0825425bbf023ef7bc96b94fdf1ec3f39eb869ff/watt-tool-70B.Q5_K_M.gguf',  # noqa
#     )
#
#     if not os.path.isfile(model_path):
#         pytest.skip(f'No model: {model_path}')
#
#     llm = LlamacppChatChoicesService(
#         ModelPath(model_path),
#     )
#
#     tool_spec = ToolSpec(
#         'get_weather',
#         params=[
#             ToolParam(
#                 'location',
#                 type=ToolDtype.of(str),
#                 desc='The location to get the weather for.',
#             ),
#         ],
#         desc='Gets the weather in the given location.',
#     )
#
#     resp = llm.invoke(Request(
#         [UserMessage('What is the weather in Seattle?')],
#         [
#             # Temperature(.1),
#             # MaxTokens(64),
#             Tool(tool_spec),
#         ],
#     ))
#
#     print(resp)
#     assert resp.v[0].m
