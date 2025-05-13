import os.path

from omlish.testing import pytest as ptu

from ....chat.messages import UserMessage
from ....chat.tools import Tool
from ....standard import ModelPath
from ....tools import ToolParam
from ....tools import ToolSpec
from ..chat import LlamacppChatService


@ptu.skip.if_cant_import('llama_cpp')
def test_llamacpp_chat_model():
    llm = LlamacppChatService()
    resp = llm(
        [UserMessage('Is water dry?')],
        # Temperature(.1),
        # MaxTokens(64),
    )
    print(resp)
    assert resp.choices[0].m.s


@ptu.skip.if_cant_import('llama_cpp')
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
        [
            ToolParam('location', 'string', desc='The location to get the weather for.'),
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
