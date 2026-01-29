import json
import typing as ta

import pytest

from omlish import check
from omlish import lang

from ..generation import GenerationParams
from ..generation import generate
from ..loading import load_model


with lang.auto_proxy_import(globals()):
    import transformers as tfm


def fix_tokenizer_output(obj: ta.Any) -> list[int]:
    if isinstance(obj, tfm.BatchEncoding):
        return check.isinstance(obj.data['input_ids'], list)
    else:
        return check.isinstance(obj, list)


@pytest.mark.not_docker_guest
@pytest.mark.high_mem
def test_tools():
    model = 'mlx-community/Qwen2.5-Coder-32B-Instruct-8bit'

    loaded = load_model(model)  # noqa

    def add(a: float, b: float) -> float:
        """
        Adds two floating point numbers.

        Args:
            a: The first number.
            b: The second number.
        """

        return a + b

    tools = {'add': add}

    messages: list[dict] = [
        {'role': 'user', 'content': 'Add 123 and 4568319.'},
    ]

    prompt = loaded.tokenization.tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tools=list(tools.values()),
    )

    prompt_cache: ta.Any = None
    # prompt_cache = mlx_lm.models.cache.make_prompt_cache(loaded.model)

    gp = GenerationParams(
        max_tokens=2048,
        **lang.opt_kw(prompt_cache=prompt_cache),
    )

    response = generate(
        loaded.model,
        loaded.tokenization,
        fix_tokenizer_output(prompt),
        gp,
        # verbose=True,
    )

    tool_open = '<tools>'
    tool_close = '</tools>'
    start_tool = response.find(tool_open) + len(tool_open)
    end_tool = response.find(tool_close)
    tool_call = json.loads(response[start_tool:end_tool].strip())
    tool_result = tools[tool_call['name']](**tool_call['arguments'])

    messages = [
        *(messages if prompt_cache is None else []),
        {'role': 'tool', 'name': tool_call['name'], 'content': tool_result},
    ]

    prompt = loaded.tokenization.tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
    )

    response = generate(  # noqa
        loaded.model,
        loaded.tokenization,
        fix_tokenizer_output(prompt),
        gp,
        # verbose=True,
    )
    assert response
