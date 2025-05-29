import os.path

import pytest

from ....chat.messages import UserMessage
from ....chat.tools import Tool
from ....standard import ModelPath
from ....tools.types import ToolDtype
from ....tools.types import ToolParam
from ....tools.types import ToolSpec
from ..chat import LlamacppChatService


@pytest.mark.not_docker_guest
@pytest.mark.high_mem
def test_llamacpp_chat_model():
    llm = LlamacppChatService()
    resp = llm(
        [UserMessage('Is water dry?')],
        # Temperature(.1),
        # MaxTokens(64),
    )
    print(resp)
    assert resp.choices[0].m.s


@pytest.mark.not_docker_guest
@pytest.mark.high_mem
def test_llamacpp_chat_model_tools():
    model_path = os.path.join(
        os.path.expanduser('~/Library/Caches/llama.cpp'),
        'bartowski_Qwen2.5-7B-Instruct-GGUF_Qwen2.5-7B-Instruct-Q4_K_M.gguf',
    )

    llm = LlamacppChatService(
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

    resp = llm(
        [UserMessage('What is the weather in Seattle?')],
        # Temperature(.1),
        # MaxTokens(64),
        Tool(tool_spec),
    )

    print(resp)
    assert resp.choices[0].m
