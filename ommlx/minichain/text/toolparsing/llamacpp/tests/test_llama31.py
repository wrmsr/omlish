from ..llama31 import parse_llama_3_1
from ..types import ChatMsg
from ..types import ChatToolCall


def test_usage():
    input_valid_builtin = '<|python_tag|> image_generator.call(prompt = "A cat wearing a hat")'
    result1 = parse_llama_3_1(input_valid_builtin, with_builtin_tools=True)
    assert result1 == ChatMsg(
        tool_calls=[
            ChatToolCall(
                name='image_generator',
                arguments='{"prompt": "A cat wearing a hat"}',
                id='call_image_generator_prompt',
            ),
        ],
    )

    input_invalid_json_builtin = '<|python_tag|> data_analyzer.call(data = {not_json: true})'
    result2 = parse_llama_3_1(input_invalid_json_builtin, with_builtin_tools=True)
    assert result2 == ChatMsg(
        content='<|python_tag|> data_analyzer.call(data = {not_json: true})',
    )

    input_generic_json = '{"name": "search_web", "parameters": {"query": "python regex"}}'
    result3 = parse_llama_3_1(input_generic_json, with_builtin_tools=True)
    assert result3 == ChatMsg(
        tool_calls=[
            ChatToolCall(
                name='search_web',
                arguments='{"query": "python regex"}',
            ),
        ],
    )

    result4 = parse_llama_3_1(input_generic_json, with_builtin_tools=False)
    assert result4 == ChatMsg(
        tool_calls=[
            ChatToolCall(
                name='search_web',
                arguments='{"query": "python regex"}',
            ),
        ],
    )

    result5 = parse_llama_3_1(input_valid_builtin, with_builtin_tools=False)
    assert result5 == ChatMsg(
        content='<|python_tag|> image_generator.call(prompt = "A cat wearing a hat")',
    )

    input_numeric_arg_builtin = '<|python_tag|> calculator.call(value = 123.45)'
    result6 = parse_llama_3_1(input_numeric_arg_builtin, with_builtin_tools=True)
    assert result6 == ChatMsg(
        tool_calls=[
            ChatToolCall(
                name='calculator',
                arguments='{"value": 123.45}',
                id='call_calculator_value',
            ),
        ],
    )

    input_boolean_arg_builtin = '<|python_tag|> feature_toggle.call(enabled = true)'
    result7 = parse_llama_3_1(input_boolean_arg_builtin, with_builtin_tools=True)
    assert result7 == ChatMsg(
        tool_calls=[
            ChatToolCall(
                name='feature_toggle',
                arguments='{"enabled": true}',
                id='call_feature_toggle_enabled',
            ),
        ],
    )

    input_spaces_builtin = '  <|python_tag|>  my_tool  .  call  (  arg  =  "value"  )  '
    result8 = parse_llama_3_1(input_spaces_builtin, with_builtin_tools=True)
    assert result8 == ChatMsg(
        tool_calls=[
            ChatToolCall(
                name='my_tool',
                arguments='{"arg": "value"}',
                id='call_my_tool_arg',
            ),
        ],
    )
