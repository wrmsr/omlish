# MIT License
#
# Copyright (c) Ollama
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
# https://github.com/ollama/ollama/blob/a7240c6d636836f0bca01790038d7194f519604b/server/model.go#L158
import dataclasses as dc
import json
import typing as ta

import jinja2.nodes
import jinja2.visitor


##


def parse_objects(s: str) -> list[dict[str, ta.Any]]:
    objs = []
    offset = 0

    while offset < len(s):
        try:
            # In Python, we can use json.JSONDecoder().raw_decode() to parse JSON at a specific position in a string
            decoder = json.JSONDecoder()
            obj, end = decoder.raw_decode(s[offset:])

            # Only append if obj is a dictionary (map in Go)
            if isinstance(obj, dict):
                objs.append(obj)
            elif isinstance(obj, list):
                for e in obj:
                    if isinstance(e, dict):
                        objs.append(e)

            # Move offset by how much we consumed
            offset += end

        except json.JSONDecodeError as e:
            """
            var obj map[string]any
            decoder := json.NewDecoder(strings.NewReader(s[offset:]))

            if err := decoder.Decode(&obj); errors.Is(err, io.EOF) || errors.Is(err, io.ErrUnexpectedEOF) {
                break
            } else if syntax := &(json.SyntaxError{}); errors.As(err, &syntax) {
                // skip over any syntax errors
                offset += int(syntax.Offset)
            } else if unmarshalType := &(json.UnmarshalTypeError{}); errors.As(err, &unmarshalType) {
                // skip over any unmarshalable types
                offset += int(unmarshalType.Offset)
            } else if err != nil {
                return nil
            """

            # if e.msg == 'Expecting value" in str(e) or "Expecting '\"'" in str(e) or "Unterminated string" in str(e):
            #     # Skip over syntax errors
            #     offset += 1
            # elif "cannot unmarshal" in str(e) or "Invalid \\escape" in str(e):
            #     # Skip over unmarshalable types
            #     offset += 1
            # elif "EOF" in str(e):
            #     # Break on EOF errors
            #     break

            # Handle syntax errors by skipping the problematic character
            if e.msg == 'Expecting value':
                # Skip over syntax errors
                offset += 1
            else:
                # Return None on unexpected errors
                raise

    return objs


##


@dc.dataclass()
class ToolCallFunctionArguments:
    args: ta.Mapping[str, ta.Any]

    def __str__(self) -> str:
        return json.dumps(self.args, indent=None, separators=(',', ':'))


@dc.dataclass()
class ToolCallFunction:
    name: str
    arguments: ToolCallFunctionArguments


@dc.dataclass()
class ToolCall:
    function: ToolCallFunction


@dc.dataclass()
class Message:
    tool_calls: ta.Sequence[ToolCall]


def parse_tool_cals(output: str, jinja_template: str) -> list[ToolCallFunction]:
    ctx = {
        'message': Message(
            tool_calls=[
                ToolCall(
                    function=ToolCallFunction(
                        name='@@name@@',
                        arguments=ToolCallFunctionArguments({
                            '@@argument@@': 1,
                        }),
                    ),
                ),
            ],
        ),
    }

    env = jinja2.Environment()  # noqa
    parsed = env.parse(jinja_template)

    class ToolCallLoopVisitor(jinja2.visitor.NodeVisitor):
        def __init__(self):
            super().__init__()

            self.tool_call_loops: list[jinja2.nodes.For] = []

        def visit_For(self, node: jinja2.nodes.For) -> None:  # noqa
            if isinstance(node.target, jinja2.nodes.Name) and node.target.name == 'tool_call':
                self.tool_call_loops.append(node)
            else:
                self.generic_visit(node)

    tclv = ToolCallLoopVisitor()
    tclv.visit(parsed)
    tcl = tclv.tool_call_loops[0]

    new_parsed = jinja2.nodes.Template(
        [tcl],
        lineno=1,
    )

    compiled = env.compile(new_parsed)
    gs = env.make_globals(None)
    tmpl = env.template_class.from_code(env, compiled, gs, None)

    ren = tmpl.render(ctx)

    tos = parse_objects(ren)

    name = ''
    arguments = ''
    for k, v in tos[0].items():
        if isinstance(v, str):
            name = k
        elif isinstance(v, dict):
            arguments = k

    response_objects = parse_objects(output)

    objs: list[dict[str, ta.Any]] = []

    def collect(o):
        if isinstance(o, dict) and all(isinstance(k, str) for k in o):
            objs.append(o)
            for v in o.values():
                collect(v)
        elif isinstance(o, list):
            for e in o:
                collect(e)

    for o in response_objects:
        collect(o)

    out: list[ToolCallFunction] = []
    for o in objs:
        n = o.get(name)
        if not isinstance(n, str):
            continue

        a = o.get(arguments)
        if not isinstance(a, dict) and all(isinstance(k, str) for k in a):  # type: ignore
            continue

        out.append(ToolCallFunction(n, ToolCallFunctionArguments(a)))  # type: ignore

    return out


##


def test_parse_objects():
    tests: list = [
        {
            'input': '[{"name": "get_current_weather", "arguments": {"format":"fahrenheit","location":"San Francisco, CA"}},{"name": "get_current_weather", "arguments": {"format":"celsius","location":"Toronto, Canada"}}]',  # noqa
            'want': [
                {'name': 'get_current_weather', 'arguments': {'format': 'fahrenheit', 'location': 'San Francisco, CA'}},
                {'name': 'get_current_weather', 'arguments': {'format': 'celsius', 'location': 'Toronto, Canada'}},
            ],
        },
        {
            'input': '<toolcall>{"name": "get_current_weather", "arguments": {"format":"fahrenheit","location":"San Francisco, CA"}} </toolcall>',  # noqa
            'want': [
                {'name': 'get_current_weather', 'arguments': {'format': 'fahrenheit', 'location': 'San Francisco, CA'}},
            ],
        },
        {
            'input': '<toolcall>{"name": "get_current_weather", "arguments": {"format":"fahrenheit","location":"San Francisco, CA"}} </toolcall> <toolcall>{"name": "get_current_weather", "arguments": {"format":"celsius","location":"Toronto, ON"}} </toolcall>',  # noqa
            'want': [
                {'name': 'get_current_weather', 'arguments': {'format': 'fahrenheit', 'location': 'San Francisco, CA'}},
                {'name': 'get_current_weather', 'arguments': {'format': 'celsius', 'location': 'Toronto, ON'}},
            ],
        },
        {
            'input': '{"name": "get_current_weather", "arguments": ',
            'want': [],
        },
    ]

    for tc in tests:
        got = parse_objects(tc['input'])
        assert got == tc['want']


JINJA_TEMPLATE = """
{%- for message in messages %}
{%- if message.role == "user" %}
{%- if loop.last and tools %}[AVAILABLE_TOOLS] {{ tools }}[/AVAILABLE_TOOLS]
{%- endif %}[INST] {% if loop.first and system %}{{ system }}

{% endif %}{{ message.content }}[/INST]
{%- elif message.role == "assistant" %}
{%- if message.content %} {{ message.content }}</s>
{%- elif message.tool_calls %}[TOOL_CALLS] [
{%- for tool_call in message.tool_calls %}{"name": "{{ tool_call.function.name }}", "arguments": {{ tool_call.function.arguments }}}
{%- endfor %}]</s>
{%- endif %}
{%- elif message.role == "tool" %}[TOOL_RESULTS] {"content": {{ message.content }}}[/TOOL_RESULTS]
{%- endif %}
{%- endfor %}
"""  # noqa


OUTPUT = ''.join([
    '[TOOL_CALLS]  ',
    '[',
    '{"name": "get_current_weather", "arguments": {"format":"fahrenheit","location":"San Francisco, CA"}},',
    '{"name": "get_current_weather", "arguments": {"format":"celsius","location":"Toronto, Canada"}}',
    ']',
])


def test_parse_tool_calls():
    tcs = parse_tool_cals(OUTPUT, JINJA_TEMPLATE)
    print(tcs)
