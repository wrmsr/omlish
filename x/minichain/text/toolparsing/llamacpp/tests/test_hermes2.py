from omlish import lang

from ..hermes2 import Hermes2ProParser
from ..types import ChatMsg
from ..types import ChatToolCall


##


def parse_hermes_2_pro(input_str: str, *, extract_reasoning: bool) -> ChatMsg:
    return Hermes2ProParser(
        extract_reasoning=extract_reasoning,
    ).parse(input_str)


def test_usage():
    test_input_1 = 'This is regular text.'
    assert parse_hermes_2_pro(test_input_1, extract_reasoning=False) == ChatMsg(
        content='This is regular text.',
    )

    test_input_2 = '<think>I need to call a tool.</think><tool_call>{"name": "get_weather", "arguments": {"location": "Paris"}}</tool_call>'  # noqa
    assert parse_hermes_2_pro(test_input_2, extract_reasoning=True) == ChatMsg(
        tool_calls=[
            ChatToolCall(
                name='get_weather',
                arguments='{"location": "Paris"}',
            ),
        ],
        reasoning_content='I need to call a tool.',
    )
    assert parse_hermes_2_pro(test_input_2, extract_reasoning=False) == ChatMsg(
        content='<think>I need to call a tool.</think>',
        tool_calls=[
            ChatToolCall(
                name='get_weather',
                arguments='{"location": "Paris"}',
            ),
        ],
    )

    test_input_3 = 'Okay, let me use the calculator: ```json\n <tool_call> {"name": "calculator", "arguments": {"expression": "2+2"} } </tool_call>\n``` The result is 4.'  # noqa
    assert parse_hermes_2_pro(test_input_3, extract_reasoning=False) == ChatMsg(
        content='Okay, let me use the calculator:  The result is 4.',
        tool_calls=[
            ChatToolCall(
                name='calculator',
                arguments='{"expression": "2+2"}',
            ),
        ],
    )

    test_input_4 = 'Calling function: <function=search>{"query": "python dataclasses"}</function>'
    assert parse_hermes_2_pro(test_input_4, extract_reasoning=False) == ChatMsg(
        content='Calling function: ',
        tool_calls=[
            ChatToolCall(
                name='search',
                arguments='{"query": "python dataclasses"}',
            ),
        ],
    )

    test_input_5 = "<think>Let's try another function format.</think> <function name=\"lookup_user\"> {\"user_id\": 123} </function> Found user."  # noqa
    assert parse_hermes_2_pro(test_input_5, extract_reasoning=True) == ChatMsg(
        content='Found user.',
        tool_calls=[
            ChatToolCall(
                name='lookup_user',
                arguments='{"user_id": 123}',
            ),
        ],
        reasoning_content="Let's try another function format.",
    )

    test_input_6 = 'Malformed: <tool_call>{"name": "test", "arguments": {}}'  # Missing closing tag
    assert parse_hermes_2_pro(test_input_6, extract_reasoning=False) == ChatMsg(
        content='Malformed: <tool_call>{"name": "test", "arguments": {}}',
        tool_calls=[
            ChatToolCall(
                name='test',
                arguments='{}',
            ),
        ],
    )

    test_input_7 = 'Text before <tool_call>{"name": "tool1", "arguments": {}}</tool_call> and text after.'  # noqa
    assert parse_hermes_2_pro(test_input_7, extract_reasoning=False) == ChatMsg(
        content='Text before and text after.',
        tool_calls=[
            ChatToolCall(
                name='tool1',
                arguments='{}',
            ),
        ],
    )

    test_input_8 = '<think>Thinking...</think>Just content, no tool call.'
    assert parse_hermes_2_pro(test_input_8, extract_reasoning=True) == ChatMsg(
        content='Just content, no tool call.',
        reasoning_content='Thinking...',
    )
    assert parse_hermes_2_pro(test_input_8, extract_reasoning=False) == ChatMsg(
        content='<think>Thinking...</think>Just content, no tool call.',
    )

    assert parse_hermes_2_pro("<tool_call>\n{\"name\": \"python\", \"arguments\": {\"code\": \"print('Hello world!')\"}}\n</tool_call>", extract_reasoning=False) == ChatMsg(  # noqa
        tool_calls=[
            ChatToolCall(
                name='python',
                arguments='{"code": "print(\'Hello world!\')"}',
            ),
        ],
    )


def test_samples():
    samples = {
        n: r.read_text()
        for n, r in lang.get_relative_resources('...tests.samples', globals=globals()).items()
        if r.is_file and n.endswith('.txt')
    }

    for n, s in sorted(samples.items(), key=lambda kv: kv[0]):
        print(n)
        print(s)
        print(parse_hermes_2_pro(s, extract_reasoning=False))
        print()
