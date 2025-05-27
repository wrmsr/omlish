r"""
mlx-community/Qwen2.5-7B-Instruct-8bit
'<tool_call>\n{{"name": "multiply", "arguments": {"a": 12234585, "b": 48838483920}}}\n</tool_call>'

mlx-community/Qwen2.5-Coder-7B-Instruct-8bit
'```xml\n<function_call>\n  {"name": "multiply", "arguments": {"a": 12234585, "b": 48838483920}}\n</function_call>\n```'
'<|im_end|>\n'

mlx-community/Qwen2.5-32B-Instruct-4bit
'<tool_call>\n{"name": "multiply", "arguments": {"a": 12234585, "b": 48838483920}}\n</tool_call>'

mlx-community/Qwen2.5-Coder-32B-Instruct-8bit
'<tools>\n{"name": "multiply", "arguments": {"a": 12234585, "b": 48838483920}}\n</tools>'

mlx-community/Qwen3-30B-A3B-6bit
'<think>\nOkay, the user wants me to multiply 12234585 by 48838483920. Let me check the tools available. There\'s a '
'multiply function that takes two numbers, a and b. So I need to call that function with these two values. I should '
'make sure the parameters are correctly formatted as numbers. Let me confirm the numbers are valid. 12234585 is a '
'positive integer, and 48838483920 is also a positive integer. No issues there. I\'ll structure the tool call with '
'these values. The function should return the product. I don\'t need to calculate it myself; the function will handle '
'the multiplication. Alright, ready to make the tool call.\n</think>\n\n<tool_call>\n{"name": "multiply", "arguments": '
'{"a": 12234585, "b": 48838483920}}\n</tool_call>'


mlx-community/Llama-3.2-1B-Instruct-4bit
'<|python_tag|>{"name": "multiply", "parameters": {"a": "12234585", "b": "48838483920"}}'

mlx-community/Llama-3.3-70B-Instruct-4bit
'{"name": "multiply", "parameters": {"a": 12234585, "b": 48838483920}}'

mlx-community/Llama-3.3-70B-Instruct-8bit
'{"type": "function", "name": "multiply", "parameters": {"a": "12234585", "b": "48838483920"}}'


mlx-community/phi-4-8bit
'To multiply 12,234,585 by 48,883,848,3920, you can perform the multiplication directly:\n\n\\[ \n12,234,585 \\times '
'48,883,848,3920 = 598,086,964,000,000,000 \n\\]\n\nSo, the product is 598,086,964,000,000,000.'

mlx-community/phi-4-mini-instruct-8bit
'The product of 12234585 and 48838483920 is 597,999,999,000,000.'


mlx-community/watt-tool-8b
'The given numbers are:\n\n1. 12234585\n2. 48838483920\n\nTo multiply these numbers, we need to follow the standard '
'multiplication procedure. Here are the steps:\n\n1. Multiply the units digit of the first number (5) with the units '
'digit of the second number (0). This gives us 0.\n2. Multiply the tens digit of the first number (4) with the tens '
'digit of the second number (8). This gives us 32.\n3. Multiply the hundreds digit of the first number (3) with the '
'hundreds digit of the second number (8). This gives us 24.\n4. Multiply the thousands digit of the first number (2) '
'with the thousands digit of the second number (8). This gives us 16.\n5. Multiply the ten thousands digit of the '
'first number (2) with the ten thousands digit of the second number (8). This gives us 16.\n6. Multiply the hundred '
'thousands digit of the first number (1) with the hundred thousands digit of the second number (8). This gives us 8.\n'
'7. Multiply the million digit of the first number (1) with the million digit of the second number (8). This gives us 8'
'.\n8. Multiply the ten million digit of the first number (2) with the ten million digit of the second number (4). '
'This gives us 8.\n9. Multiply the hundred million digit of the first number (2) with the hundred million digit of the '
'second number (8). This gives us 16.\n10. Multiply the billion digit of the first number (3) with the billion digit '
'of the second number (8). This gives us 24.\n11. Multiply the ten billion digit of the first number (2) with the ten '
'billion digit of the second number (8). This gives us 16.\n12. Multiply the hundred billion digit of the first number '
'(4) with the hundred billion digit of the second number (8). This gives us 32.\n13. Multiply the thousand billion '
'digit of the first number (3) with the thousand billion digit of the second number (8). This gives us 24.\n14. '
'Multiply the ten thousand billion digit of the first number (2) with the ten thousand billion digit of the second '
'number (4). This gives us 8.\n15. Multiply the hundred thousand billion digit of the first number (2) with the '
'hundred thousand billion digit of the second number (8). This gives us 16.\n16. Multiply the million billion digit of '
'the first number (1) with the million billion digit of the second number (8). This gives us 8.\n17. Multiply the ten '
'million billion digit of the first number (2) with the ten million billion digit of the second number (4). This gives '
'us 8.\n18. Multiply the hundred million billion digit of the first number (2) with the hundred million billion digit '
'of the second number (8). This gives us 16.\n19. Multiply the billion billion digit of the first number (3) with the '
'billion billion digit of the second number (8). This gives us 24.\n20. Multiply the ten billion billion digit of the '
'first number (2) with the ten billion billion digit of the second number (8). This gives us 16.\n21. Multiply the '
'hundred billion billion digit of the first number (4) with the hundred billion billion digit of the second number '
'(8). This gives us 32.\n22. Multiply the thousand billion billion digit of the first number (3) with the thousand '
'billion billion digit of the second number (8). This gives us 24.\n23. Multiply the ten thousand billion billion '
'digit of the first number (2) with the ten thousand billion billion digit of the second number (4). This gives us 8.\n'
'24. Multiply the hundred thousand billion billion digit of the first number (2) with the hundred thousand billion '
'billion digit of the second number (8). This gives us 16.\n25. Multiply the million billion billion digit of the '
'first number (1) with the million billion billion digit of the second number (8). This gives us 8.\n26. Multiply the '
'ten million billion billion digit of the first number (2) with the ten million billion billion digit of the second '
'number (4). This gives us 8.\n27. Multiply the hundred million billion billion digit of the first number (2) with the '
'hundred million billion billion digit of the second number (8). This gives us 16.\n28. Multiply the billion billion '
'billion digit of the first number (3) with the billion billion billion digit of the second number (8). This gives us '
'24.\n29. Multiply the ten billion billion billion digit of the first number (2) with the ten billion billion billion '
'digit of the second number (8). This gives us 16.\n30. Multiply the hundred billion billion billion digit of the '
'first number (4) with the hundred billion billion billion digit of the second number (8). This gives us 32.\n31. '
'Multiply the thousand billion billion billion digit of the first number (3) with the thousand billion billion billion '
'digit of the second number (8). This gives us 24.\n32. Multiply the ten thousand billion billion billion digit of the '
'first number (2) with the ten thousand billion billion billion digit of the second number (4). This gives us 8.\n33. '
'Multiply the hundred thousand billion billion billion digit of the first number (2) with the hundred thousand billion '
'billion billion digit of the second number (8). This gives us 16.\n34. Multiply the million billion billion billion '
'digit of the first number (1) with the million billion billion billion digit of the second number (8). This gives us '
'8.\n35. Multiply the ten million billion billion billion digit of the first number (2) with the ten million billion '
'billion billion digit of the second number (4). This gives us 8.\n36. Multiply the hundred million billion billion '
'billion digit of the first number (2) with the hundred million billion billion billion digit of the second number '
'(8). This gives us 16.\n37. Multiply the billion billion billion billion digit of the first number (3) with the '
'billion billion billion billion digit of the second number (8). This gives us 24.\n38. Multiply the ten billion '
'billion billion billion digit of the first number (2) with the ten billion billion billion billion digit of the '
'second number (8). This gives us 16.\n39. Multiply the hundred billion billion billion billion digit of the first '
'number (4) with the hundred billion billion billion billion digit of the second number (8). This gives us 32.\n40. '
'Multiply the thousand billion billion billion billion digit of the first number (3) with the thousand billion billion '
'billion billion digit of the second number (8). This gives us 24.\n41. Multiply the ten thousand billion billion '
'billion billion digit of the first number (2) with the ten thousand billion billion billion billion digit of the '
'second number (4). This gives us 8.\n42. Multiply the hundred thousand billion billion billion billion digit of the '
'first number (2) with the hundred thousand billion billion billion billion digit of the second number (8). This gives '
'us 16.\n43. Multiply the million billion billion billion billion digit of the first number (1) with the million '
'billion billion billion billion digit of the second number (8). This gives us 8.\n44. Multiply the ten million '
'billion billion billion billion digit of the first number (2) with the ten million billion billion billion billion '
'digit of the second number (4). This gives us 8.\n45. Multiply the hundred million billion billion billion billion '
'digit of the first number (2) with the hundred million billion billion billion billion digit of the second number '
'(8). This gives us 16.\n46. Multiply the billion billion billion billion billion digit of the first number (3) with '
'the billion billion billion billion billion digit of the second number (8). This gives us 24.\n47. Multiply the ten '
'billion billion billion billion billion digit of the first number (2) with the ten billion billion billion billion '
'billion digit of the second number (8). This gives us 16.\n48. Multiply the hundred billion billion billion billion '
'billion digit of the first number (4) with the hundred billion billion billion billion billion digit of the second '
'number (8). This gives us 32.\n49. Multiply the thousand billion billion billion billion billion digit of the first '
'number (3) with the thousand billion billion billion billion billion digit of the second number (8). This gives us '
'24.\n50. Multiply the ten thousand billion billion billion billion billion digit of the first number (2) with the ten '
'thousand billion billion billion billion billion digit of the second number (4). This gives us 8.\n51. Multiply the '
'hundred thousand billion billion billion billion billion digit of the first number (2) with the hundred thousand '
'billion billion billion billion billion digit of the second number (8). This gives us 16.\n52. Multiply the million '
'billion billion billion billion billion digit of the first number (1) with the million billion billion billion '
'billion billion digit of the second number (8). This gives us 8.\n53. Multiply the ten million billion billion '
'billion billion billion digit of the first number (2) with the ten million billion billion billion billion billion '
'digit of the second number (4). This gives us 8.\n54. Multiply the hundred million billion billion billion billion '
'billion digit of the first number (2) with the hundred million billion billion billion billion billion digit of the '
'second number (8). This gives us 16.\n55. Multiply the billion billion billion billion billion billion digit of the '
'first number (3) with the billion billion billion billion billion billion digit of the second number (8). This gives '
'us 24.\n56. Multiply the ten billion billion billion billion billion billion digit of the first number (2) with the '
'ten billion billion billion billion billion billion digit of the second number (8). This gives us 16'


mlx-community/DeepSeek-Coder-V2-Lite-Instruct-8bit
'To multiply 12234585 and 48838483920, we can follow these steps:\n\n1. **Set up the multiplication**: Write the '
'numbers in a column format for clarity.\n\n```\n      12234585\n   × 48838483920\n```\n\n2. **Multiply each digit of '
'the first number by each digit of the second number**: Start from the rightmost digit of the second number and move '
'left.\n\n- **Multiplying 12234585 by the rightmost digit (0)**:\n  ```\n      12234585\n   ×       0\n  ---------'
'\n      00000000\n  ```\n\n- **Multiplying 12234585 by the next digit (2)**:\n  ```\n      12234585\n   ×       2'
'\n  ---------\n     24469170\n  ```\n\n- **Multiplying 12234585 by the next digit (3)**:\n  ```\n      12234585\n   '
'×       3\n  ---------\n     36703755\n  ```\n\n- **Multiplying 12234585 by the next digit (8)**:\n  ```\n      '
'12234585\n   ×       8\n  ---------\n    97876680\n  ```\n\n- **Multiplying 12234585 by the next digit (4)**:\n  ```'
'\n      12234585\n   ×       4\n  ---------\n    48938340\n  ```\n\n- **Multiplying 12234585 by the next digit (8)**:'
'\n  ```\n      12234585\n   ×       8\n  ---------\n    97876680\n  ```\n\n- **Multiplying 12234585 by the next digit '
'(3)**:\n  ```\n      12234585\n   ×       3\n  ---------\n     36703755\n  ```\n\n- **Multiplying 12234585 by the '
'next digit (8)**:\n  ```\n      12234585\n   ×       8\n  ---------\n    97876680\n  ```\n\n- **Multiplying 12234585 '
'by the next digit (4)**:\n  ```\n      12234585\n   ×       4\n  ---------\n    48938340\n  ```\n\n3. **Add up all '
'the partial products**:\n  ```\n    00000000\n  + 24469170\n  + 36703755\n  + 97876680\n  + 48938340\n  + 97876680'
'\n  + 36703755\n  + 97876680\n  + 48938340\n  ---------\n   5960498434560\n  ```\n\n4. **Combine the results**: The '
'final product of 12234585 and 48838483920 is 5960498434560.\n\nSo, the answer is $\\boxed{5960498434560}$.'

mlx-community/DeepSeek-R1-Distill-Llama-70B-8bit
"First, I need to multiply the two large numbers, 12,234,585 and 48,838,483,920. To make this manageable, I'll break "
"down the larger number into smaller, more workable parts.\n\nI'll start by expressing 48,838,483,920 as the sum of "
"40,000,000,000 and 8,838,483,920. This allows me to handle each part separately.\n\nNext, I'll multiply 12,234,585 by "
"40,000,000,000. This involves multiplying 12,234,585 by 4 and then adding 10 zeros to the result, which gives me "
"488,838,483,400,000,000,000.\n\nThen, I'll multiply 12,234,585 by 8,838,483,920. To simplify this, I'll break it down "
"further into multiplying by 8,000,000,000, 838,483,920, and so on, ensuring each step is clear and manageable.\n\n"
"After calculating each part, I'll add the results together to obtain the final product. This step-by-step approach "
"helps in handling the multiplication of large numbers accurately.\n</think>\n\nTo multiply the numbers **12,234,585** "
"and **48,838,483,920**, follow these steps:\n\n### Step 1: Break Down the Numbers\nFirst, let's break down the larger "
"number to simplify the multiplication:\n\n\\[\n48,\\!838,\\!483,\\!920 = 40,\\!000,\\!000,\\!000 + 8,\\!838,\\!483,\\"
""!920\n\\]\n\n### Step 2: Multiply Each Part Separately\n\n1. **Multiply by 40,000,000,000:**\n\n\\[\n12,\\!234,\\"
"!585 \\times 40,\\!000,\\!000,\\!000 = 12,\\!234,\\!585 \\times 4 \\times 10,\\!000,\\!000,\\!000\n\\]\n\n\\[\n12,\\"
"!234,\\!585 \\times 4 = 48,\\!938,\\!340\n\\]\n\n\\[\n48,\\!938,\\!340 \\times 10,\\!000,\\!000,\\!000 = 489,\\!383,\\"
"!400,\\!000,\\!000,\\!000\n\\]\n\n2. **Multiply by 8,838,483,920:**\n\n\\[\n12,\\!234,\\!585 \\times 8,\\!838,\\!483,"
"\\!920\n\\]\n\nThis multiplication can be further broken down, but for simplicity, we'll calculate it directly:\n\n\\["
"\n12,\\!234,\\!585 \\times 8,\\!838,\\!483,\\!920 = 108,\\!147,\\!142,\\!337,\\!200,\\!800\n\\]\n\n### Step 3: Add "
"the Results Together\n\n\\[\n489,\\!383,\\!400,\\!000,\\!000,\\!000 + 108,\\!147,\\!142,\\!337,\\!200,\\!800 = 597,\\"
"!530,\\!542,\\!337,\\!200,\\!800\n\\]\n\n### Final Answer\n\n\\[\n\\boxed{597,\\!530,\\!542,\\!337,\\!200,\\!800}\n\\]"
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

from .... import minichain as mc
from ....minichain.tools.jsonschema import build_tool_spec_json_schema
from ....minichain.tools.types import PrimitiveToolDtype


##


def multiply(a: float, b: float) -> float:
    """
    A function that multiplies two numbers

    Args:
        a: The first number to multiply
        b: The second number to multiply
    """

    return a * b


MULTIPLY_TOOL = mc.ToolSpec(
    'multiply',
    params=[
        mc.ToolParam(
            'a',
            type=PrimitiveToolDtype.of(float),
            desc='The first number to multiply',
            required=True,
        ),
        mc.ToolParam(
            'b',
            type=PrimitiveToolDtype.of(float),
            desc='The second number to multiply',
            required=True,
        ),
    ],
    desc='A function that multiplies two numbers',
)

MULTIPLY_TOOL_JSON_SCHEMA = build_tool_spec_json_schema(
    MULTIPLY_TOOL,
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


@pytest.mark.skip
@ptu.skip.if_cant_import('mlx_lm')
def test_dump_chat_templates():
    tools = {'multiply': multiply}

    messages = [{'role': 'user', 'content': 'Multiply 12234585 and 48838483920.'}]

    import mlx.nn  # noqa
    import mlx_lm.utils

    for checkpoint in [
        'mlx-community/Qwen2.5-7B-Instruct-8bit',
        'mlx-community/Qwen2.5-Coder-7B-Instruct-8bit',
        'mlx-community/Qwen2.5-32B-Instruct-4bit',
        'mlx-community/Qwen2.5-Coder-32B-Instruct-8bit',

        'mlx-community/Qwen3-30B-A3B-6bit',

        'mlx-community/Llama-3.2-1B-Instruct-4bit',
        'mlx-community/Llama-3.3-70B-Instruct-4bit',
        'mlx-community/Llama-3.3-70B-Instruct-8bit',

        'mlx-community/phi-4-8bit',
        'mlx-community/phi-4-mini-instruct-8bit',

        'mlx-community/watt-tool-8b',

        'mlx-community/DeepSeek-Coder-V2-Lite-Instruct-8bit',
        'mlx-community/DeepSeek-R1-Distill-Llama-70B-8bit',
    ]:
        model: mlx.nn.Module
        tokenizer: mlx_lm.utils.TokenizerWrapper
        model, tokenizer = mlx_lm.load(path_or_hf_repo=checkpoint)

        prompt = tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tools=list(tools.values()),
        )

        response = mlx_lm.generate(
            model=model,
            tokenizer=tokenizer,
            prompt=prompt,
            max_tokens=2048,
        )

        print(checkpoint)
        print(repr(response))
        print()


@pytest.mark.not_docker_guest
@pytest.mark.high_mem
@ptu.skip.if_cant_import('mlx_lm')
def test_mlx():
    import mlx.nn  # noqa
    import mlx_lm.models.cache
    import mlx_lm.utils

    tools = {'multiply': multiply}

    # 597_518_582_790_373_200
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
    tool_open_pos = response.find(tool_open)
    assert tool_open_pos >= 0
    start_tool = tool_open_pos + len(tool_open)
    tool_close_pos = response.find(tool_close, start_tool)
    assert tool_close_pos > 0
    end_tool = tool_close_pos
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
