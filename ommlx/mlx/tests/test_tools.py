import json
import typing as ta

import pytest

from omlish import lang
from omlish.testing import pytest as ptu

from ..generation import generate
from ..loading import load_model


if ta.TYPE_CHECKING:
    import mlx_lm.models.cache  # noqa
else:
    mlx_lm = lang.proxy_import('mlx_lm', extras=['models.cache'])


@pytest.mark.not_docker_guest
@ptu.skip.if_cant_import('mlx_lm')
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

    prompt = loaded.check_pre_trained_tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tools=list(tools.values()),
    )

    prompt_cache: ta.Any = None
    # prompt_cache = mlx_lm.models.cache.make_prompt_cache(loaded.model)

    response = generate(
        model=loaded.model,
        tokenizer=loaded.tokenizer,
        prompt=prompt,  # type: ignore
        max_tokens=2048,
        # verbose=True,
        **lang.opt_kw(prompt_cache=prompt_cache),
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

    prompt = loaded.check_pre_trained_tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
    )

    response = generate(  # noqa
        model=loaded.model,
        tokenizer=loaded.tokenizer,
        prompt=prompt,  # type: ignore
        max_tokens=2048,
        # verbose=True,
        **lang.opt_kw(prompt_cache=prompt_cache),
    )
    assert response
