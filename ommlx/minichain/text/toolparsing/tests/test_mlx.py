"""
mlx-community/Qwen2.5-7B-Instruct-8bit
'<tool_call>\n{{"name": "multiply", "arguments": {"a": 12234585, "b": 48838483920}}}\n</tool_call>'

mlx-community/Qwen2.5-Coder-7B-Instruct-8bit
'```xml\n<function_call>\n  {"name": "multiply", "arguments": {"a": 12234585, "b": 48838483920}}\n</function_call>\n```<|im_end|>\n'

mlx-community/Qwen2.5-32B-Instruct-4bit
'<tool_call>\n{"name": "multiply", "arguments": {"a": 12234585, "b": 48838483920}}\n</tool_call>'

mlx-community/Qwen2.5-Coder-32B-Instruct-8bit
'<tools>\n{"name": "multiply", "arguments": {"a": 12234585, "b": 48838483920}}\n</tools>'
"""  # noqa
# Copyright © 2025 Apple Inc.
# MIT License
#
# Copyright © 2023 Apple Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
import json

import pytest

from omlish.testing import pytest as ptu

from ....tools import ToolParam
from ....tools import ToolSpec
from ....tools import build_tool_spec_json_schema


##


def multiply(a: float, b: float) -> float:
    """
    A function that multiplies two numbers

    Args:
        a: The first number to multiply
        b: The second number to multiply
    """

    return a * b


MULTIPLY_TOOL = ToolSpec(
    'multiply',
    [
        ToolParam(
            'a',
            'number',
            desc='The first number to multiply',
            required=True,
        ),
        ToolParam(
            'b',
            'number',
            desc='The second number to multiply',
            required=True,
        ),
    ],
    desc='A function that multiplies two numbers',
)

MULTIPLY_TOOL_JSON_SCHEMA = build_tool_spec_json_schema(
    MULTIPLY_TOOL,
    omit_additional_properties_keyword=True,
)


def test_multiply_tool_json_schema():
    assert MULTIPLY_TOOL_JSON_SCHEMA == {
        'description': 'A function that multiplies two numbers',
        'name': 'multiply',
        'parameters': {
            'properties': {
                'a': {
                    'description': 'The first number to multiply',
                    'type': 'number',
                },
                'b': {
                    'description': 'The second number to multiply',
                    'type': 'number',
                },
            },
            'required': ['a', 'b'],
            'type': 'object',
        },
    }


##


# def test_barf():
#     tools = {'multiply': multiply}
#
#     messages = [{'role': 'user', 'content': 'Multiply 12234585 and 48838483920.'}]
#
#     import mlx.nn  # noqa
#     import mlx_lm.utils
#
#     for checkpoint in [
#         'mlx-community/Qwen2.5-7B-Instruct-8bit',
#         'mlx-community/Qwen2.5-Coder-7B-Instruct-8bit',
#         'mlx-community/Qwen2.5-32B-Instruct-4bit',
#         'mlx-community/Qwen2.5-Coder-32B-Instruct-8bit',
#     ]:
#         model: mlx.nn.Module
#         tokenizer: mlx_lm.utils.TokenizerWrapper
#         model, tokenizer = mlx_lm.load(path_or_hf_repo=checkpoint)
#
#         prompt = tokenizer.apply_chat_template(
#             messages,
#             add_generation_prompt=True,
#             tools=list(tools.values()),
#         )
#
#         response = mlx_lm.generate(
#             model=model,
#             tokenizer=tokenizer,
#             prompt=prompt,
#             max_tokens=2048,
#         )
#
#         print(checkpoint)
#         print(repr(response))
#         print()


@pytest.mark.not_docker_guest
@ptu.skip.if_cant_import('mlx_lm')
def test_mlx():
    import mlx.nn  # noqa
    import mlx_lm.models.cache
    import mlx_lm.utils

    tools = {'multiply': multiply}

    messages: list[dict] = [{'role': 'user', 'content': 'Multiply 12234585 and 48838483920.'}]

    # checkpoint = 'mlx-community/Qwen2.5-7B-Instruct-8bit'
    # checkpoint = 'mlx-community/Qwen2.5-Coder-7B-Instruct-8bit'
    # checkpoint = 'mlx-community/Qwen2.5-32B-Instruct-4bit'
    checkpoint = 'mlx-community/Qwen2.5-Coder-32B-Instruct-8bit'

    model: mlx.nn.Module
    tokenizer: mlx_lm.utils.TokenizerWrapper
    model, tokenizer = mlx_lm.load(path_or_hf_repo=checkpoint)

    prompt = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tools=list(tools.values()),
    )

    prompt_cache = mlx_lm.models.cache.make_prompt_cache(model)

    response = mlx_lm.generate(
        model=model,
        tokenizer=tokenizer,
        prompt=prompt,
        max_tokens=2048,
        verbose=True,
        prompt_cache=prompt_cache,
    )

    tool_open = '<tools>'
    tool_close = '</tools>'
    start_tool = response.find(tool_open) + len(tool_open)
    end_tool = response.find(tool_close)
    tool_call = json.loads(response[start_tool:end_tool].strip())
    tool_result = tools[tool_call['name']](**tool_call['arguments'])

    messages = [{'role': 'tool', 'name': tool_call['name'], 'content': tool_result}]
    prompt = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
    )

    response = mlx_lm.generate(
        model=model,
        tokenizer=tokenizer,
        prompt=prompt,
        max_tokens=2048,
        verbose=True,
        prompt_cache=prompt_cache,
    )

    print(response)
