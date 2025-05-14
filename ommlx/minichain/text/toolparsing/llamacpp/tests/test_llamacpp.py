"""
Primary authored by gemini-2.5-pro
"""
# MIT License
#
# Copyright (c) 2023-2024 The ggml authors
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
# https://github.com/ggml-org/llama.cpp/blob/cf0a43bb6490bd49344775abb22ba26f8047cb54/common/chat.cpp#L1448
import dataclasses as dc
import json
import logging
import re
import typing as ta

from omlish import lang


log = logging.getLogger(__name__)


##


@dc.dataclass()
class ChatToolCall:
    name: str
    arguments: str  # Arguments are stored as a JSON string
    id: str = ''    # Optional ID for the tool call


@dc.dataclass()
class ChatMsg:
    content: str = ''
    tool_calls: list[ChatToolCall] = dc.field(default_factory=list)
    reasoning_content: str = ''


##


def _parse_json_from_string(s: str, index: int) -> tuple[ta.Any | None, int]:
    """
    Attempts to parse a JSON object or string starting at index. Returns the parsed object and the index immediately
    after the parsed JSON. Returns (None, index) if parsing fails right away. Uses json.JSONDecoder.raw_decode for
    robust parsing within larger strings.
    """

    decoder = json.JSONDecoder()
    try:
        # Skip leading whitespace before attempting decode
        while index < len(s) and s[index].isspace():
            index += 1
        if index == len(s):
            return None, index  # No JSON found
        obj, end_index = decoder.raw_decode(s, index)
        return obj, end_index

    except json.JSONDecodeError:
        # raw_decode failed, means no valid JSON starts at index (after whitespace)
        return None, index

    except IndexError:  # Reached end of string unexpectedly
        return None, index


def process_tool_call(tool_call_data: dict[str, ta.Any]) -> ChatToolCall:
    """Processes a dictionary (parsed from JSON) into a ChatToolCall."""

    arguments = tool_call_data.get('arguments', {})
    # Ensure arguments are always stored as a string
    arguments_str = json.dumps(arguments) if not isinstance(arguments, str) else arguments

    return ChatToolCall(
        name=tool_call_data.get('name', ''),
        arguments=arguments_str,
        id=tool_call_data.get('id', ''),
    )


##


def handle_think_tag_prelude(
    input_str: str,
    extract_reasoning: bool,
    rest_parser: ta.Callable[[str], ChatMsg],
) -> ChatMsg:
    """Checks for <think>...</think> tags at the beginning of the input and processes the rest using rest_parser."""

    # Regex to capture optional <think> block and the rest of the content. Handles potential whitespace around tags.
    # DOTALL allows '.' to match newline characters.
    reasoning_regex = re.compile(
        r'^\s*(?:<think>([\s\S]*?)</think>\s*)?([\s\S]*)$',
        re.DOTALL,
    )
    match = reasoning_regex.match(input_str)

    if match:
        thinking_content = match.group(1)  # Content inside <think> tags (can be None)
        rest_content = match.group(2)      # Content after <think> tags

        # Parse the rest of the content
        msg = rest_parser(rest_content or '')  # Pass empty string if rest is None

        if thinking_content is not None:
            reasoning_text = thinking_content.strip()
            if extract_reasoning:
                msg.reasoning_content = reasoning_text
            elif reasoning_text:
                # Prepend the think block if not extracting and it's not empty
                msg.content = f'<think>{reasoning_text}</think>{msg.content}'
        return msg

    else:
        # Should not happen with this regex unless input_str is not a string, but handle defensively.
        log.error('Reasoning regex failed to match input.')
        return rest_parser(input_str)


def parse_hermes_2_pro(
        input_str: str,
        *,
        extract_reasoning: bool,
) -> ChatMsg:
    """
    Parses the Hermes 2 Pro format, handling <think> tags and various tool call syntaxes (JSON objects, <function>
    tags).
    """

    def _parse_hermes_content(content_to_parse: str) -> ChatMsg:
        """Inner function to parse the content after <think> tags are handled."""

        msg = ChatMsg()
        current_pos = 0
        end_pos = len(content_to_parse)

        # Regex to find potential tool calls (JSON or function tags). Combined the variations into one regex with
        # alternatives. Using non-capturing groups (?:...) where possible. DOTALL allows '.' to match newlines within
        # arguments etc.
        open_regex = re.compile(
            # Group 1: Optional code block start (e.g., ```json\n)
            r'('
            r'```(?:xml|json)?\s*\n\s*'
            r')?'

            # Group 2: Optional opening tag
            r'('
            r'<tool_call>'
            r'|<function_call>'
            r'|<tool>'
            r'|<tools>'
            r'|<response>'
            r'|<json>'
            r'|<xml>'
            r'|<JSON>'
            r')?'

            # Group 3: JSON object starting with "name"
            r'(\s*\{\s*\"name\"\s*:[\s\S]*)'

            r'|'

            # Group 4: <function=name>
            r'(?:<function=([^>]+)>'

            # Group 5: <function name="name">
            r'|<function name=\"([^\"]+)\">)'

            # Group 6: Arguments for function tag + rest
            r'([\s\S]*)',

            re.DOTALL,
        )

        while current_pos < end_pos:
            # Search from the current position
            match = open_regex.search(content_to_parse, current_pos)

            if not match:
                # No more potential tool calls found
                msg.content += content_to_parse[current_pos:]
                break

            # Add content before this potential tool call
            msg.content += content_to_parse[current_pos:match.start()]

            # Process the match
            block_start = match.group(1) or ''
            block_end = '```' if block_start else ''

            open_tag = match.group(2) or ''
            json_candidate_text = match.group(3)  # Potential JSON starting with { "name": ...
            func_name1 = match.group(4)           # <function=...> name
            func_name2 = match.group(5)           # <function name="..."> name

            tool_call_processed = False
            next_parse_pos = -1  # Where to continue parsing after a successful tool call

            try:
                if json_candidate_text:
                    # Case 1: Looks like a JSON object possibly within tags
                    close_tag = f'</{open_tag[1:]}' if open_tag else ''

                    # Start parsing JSON from the beginning of group 3 relative to the match start
                    json_obj, json_end_idx_rel = _parse_json_from_string(match.group(0), match.start(3) - match.start())
                    json_end_idx_abs = json_end_idx_rel + match.start()

                    # Check if it's a valid tool call structure
                    if isinstance(json_obj, dict) and 'name' in json_obj and 'arguments' in json_obj:
                        # Valid tool call found
                        msg.tool_calls.append(process_tool_call(json_obj))
                        tool_call_processed = True
                        pos_after_json = json_end_idx_abs

                        # Check for closing tags
                        remaining_str = content_to_parse[pos_after_json:]
                        remaining_str_lstrip = remaining_str.lstrip()
                        advance = len(remaining_str) - len(remaining_str_lstrip)
                        pos_after_json += advance  # Account for stripped whitespace

                        if close_tag:
                            if content_to_parse.startswith(close_tag, pos_after_json):
                                pos_after_json += len(close_tag)
                            else:
                                raise ValueError(f"Missing close tag '{close_tag}'")  # noqa

                        remaining_str = content_to_parse[pos_after_json:]
                        remaining_str_lstrip = remaining_str.lstrip()
                        advance = len(remaining_str) - len(remaining_str_lstrip)
                        pos_after_json += advance  # Account for stripped whitespace

                        if block_end:
                            if content_to_parse.startswith(block_end, pos_after_json):
                                pos_after_json += len(block_end)
                            else:
                                raise ValueError(f"Missing block end '{block_end}'")  # noqa

                        next_parse_pos = pos_after_json

                    # else: Not a valid tool call JSON, treat whole match as content later

                elif func_name1 or func_name2:
                    # Case 2: Looks like a <function...> tag
                    function_name = func_name1 or func_name2
                    close_tag = '</function>'

                    # Arguments start at the beginning of group 6 relative to match start
                    args_start_idx_abs = match.start(6)
                    arguments_obj, args_end_idx_abs = _parse_json_from_string(content_to_parse, args_start_idx_abs)

                    if arguments_obj is not None:
                        # Successfully parsed arguments
                        tool_data = {
                            'name': function_name,
                            'arguments': arguments_obj,
                        }
                        msg.tool_calls.append(process_tool_call(tool_data))
                        tool_call_processed = True
                        pos_after_args = args_end_idx_abs

                        # Check for closing tags (</function> and potential ```)
                        remaining_str = content_to_parse[pos_after_args:]
                        remaining_str_lstrip = remaining_str.lstrip()
                        advance = len(remaining_str) - len(remaining_str_lstrip)
                        pos_after_args += advance

                        if close_tag:
                            if content_to_parse.startswith(close_tag, pos_after_args):
                                pos_after_args += len(close_tag)
                            else:
                                raise ValueError(f"Missing close tag '{close_tag}'")  # noqa

                        remaining_str = content_to_parse[pos_after_args:]
                        remaining_str_lstrip = remaining_str.lstrip()
                        advance = len(remaining_str) - len(remaining_str_lstrip)
                        pos_after_args += advance

                        if block_end:
                            if content_to_parse.startswith(block_end, pos_after_args):
                                pos_after_args += len(block_end)
                            else:
                                raise ValueError(f"Missing block end '{block_end}'")  # noqa

                        next_parse_pos = pos_after_args

                    # else: Failed to parse arguments JSON, treat whole match as content later

            except Exception as e:  # noqa
                # If parsing tool call or checking tags fails, treat block as content
                log.warning('Failed processing potential tool call: %r. Treating as content: %r', e, match.group(0))  # noqa
                tool_call_processed = False  # Ensure it falls through to content append

            # Update position
            if tool_call_processed and next_parse_pos != -1:
                # Successfully parsed a tool call, continue after it
                current_pos = next_parse_pos
            else:
                # Match didn't yield a valid/complete tool call, treat the whole match as content and continue searching
                # *after* this match.
                msg.content += match.group(0)
                current_pos = match.end()

        # Strip final content if needed.
        # msg.content = msg.content.strip()
        return msg

    try:
        # First, handle the optional <think> prelude
        return handle_think_tag_prelude(input_str, extract_reasoning, _parse_hermes_content)

    except Exception:  # noqa
        log.exception('Failed to parse Hermes 2 Pro input: Input: %r', input_str)

        # Return a message with the original input as content on failure
        msg = ChatMsg(content=input_str)
        return msg


def parse_json_tool_calls(
        input_str: str,
        trigger_opt: re.Pattern | None = None,
        function_regex: re.Pattern = re.compile(r''),  # Must be provided if used
        close_regex: re.Pattern = re.compile(r''),  # Must be provided if used
        allow_raw_python: bool = False,
) -> ChatMsg:
    """
    Parses input assuming tool calls are marked by function_regex, contain JSON, and end with close_regex. An optional
    trigger_opt starts the process.

    Args:
        input_str: The string potentially containing tool calls.
        trigger_opt: Optional regex to find the start of the tool call section.
        function_regex: Regex with one capture group for the function name.
        close_regex: Regex marking the end of the tool call arguments.
        allow_raw_python: Special handling for raw python code blocks.

    Returns:
        A ChatMsg object with parsed content and tool calls.
    """

    result = ChatMsg()
    current_pos = 0
    end_pos = len(input_str)

    if trigger_opt:
        match = trigger_opt.search(input_str)
        if not match:
            result.content = input_str
            return result
        result.content = input_str[:match.start()]
        current_pos = match.end()
    else:
        result.content = ''  # Start with empty content if no trigger

    while current_pos < end_pos:
        # Find the next function call start
        func_match = function_regex.search(input_str, current_pos)
        if not func_match:
            # No more function calls found, append the rest
            result.content += input_str[current_pos:]
            break

        # Append content before this function call
        result.content += input_str[current_pos:func_match.start()]

        name = func_match.group(1)  # Assumes group 1 is the name
        parse_start_pos = func_match.end()  # Start looking for JSON after the name match

        # Try to parse JSON arguments
        arguments_obj, next_pos = _parse_json_from_string(input_str, parse_start_pos)

        if arguments_obj is not None:
            # Successfully parsed JSON, now look for the closing pattern
            close_match = close_regex.search(input_str, next_pos)
            if not close_match:
                # This should ideally not happen if format is guaranteed, but handle defensively. Treat rest as content?
                # Or error? C++ throws, Python can raise or log and treat as content. Let's treat the rest as content
                # for robustness.
                log.warning(
                    'Malformed input: Missing closing pattern after JSON for tool %r. Input: %s',
                    name,
                    input_str[current_pos:],
                )
                result.content += input_str[func_match.start():]  # Add the failed block as content
                current_pos = end_pos  # Stop processing
                break

            # Found JSON and close pattern
            arguments_str = json.dumps(arguments_obj) if not isinstance(arguments_obj, str) else arguments_obj
            result.tool_calls.append(ChatToolCall(name=name, arguments=arguments_str, id=''))
            current_pos = close_match.end()  # Move past the closing pattern

        elif allow_raw_python and name == 'python':
            # Special case: if JSON parsing fails but it's a 'python' tool, capture remaining text as code. This assumes
            # close_regex isn't needed. NOTE: C++ version captures till end. This might need refinement depending on
            # exact expected format. Does 'python' have a closer? Assuming it consumes the rest of the string here.
            code_content = input_str[parse_start_pos:]
            arguments_obj = {'code': code_content}
            arguments_str = json.dumps(arguments_obj)
            result.tool_calls.append(ChatToolCall(name=name, arguments=arguments_str, id=''))
            current_pos = end_pos  # Consumed the rest
            break
        else:
            # Failed to parse JSON, and not the special python case. Treat the function regex match and subsequent text
            # as literal content. Or raise error like C++? Let's log and add as content.
            log.warning(
                "Failed to parse JSON arguments for tool '%s'. Input: %s",
                name,
                input_str[current_pos:],
            )
            result.content += input_str[func_match.start():]  # Add the failed block
            current_pos = end_pos  # Stop processing
            break

    # If tool calls were generated, check if there's non-whitespace content left
    if result.tool_calls and result.content.strip():
        log.warning('Content found along with tool calls: %r', result.content)
        # Original C++ clears content here. Let's keep it but log warning. If clearing is desired uncomment below:
        # result.content = ""

    return result


class Llama31ToolExecParser:
    # std::regex("\\s*\\{\\s*(?:\"type\"\\s*:\\s*\"function\"\\s*,\\s*)?\"name\"\\s*:\\s*\"([^\"]+)\"\\s*,\\s*\"parameters\"\\s*: ");  # noqa
    FUNCTION_REGEX_PATTERN: ta.ClassVar[re.Pattern[str]] = re.compile(
        r'\s*\{\s*(?:"type"\s*:\s*"function"\s*,\s*)?"name"\s*:\s*"([^"]+)"\s*,\s*"parameters"\s*:\s*',
    )

    # static const std::regex close_regex("\\}\\s*");
    CLOSE_REGEX_PATTERN: ta.ClassVar[re.Pattern[str]] = re.compile(r'\}\s*')

    # std::regex("<\\|python_tag\\|>\\s*([^.(]+)\\s*\\.\\s*call\\s*\\(\\s*([\\w]+)\\s*=\\s*([\\s\\S]*?)\\)");
    # Group 1: tool name (e.g., "my_tool" from "my_tool.call")
    # Group 2: argument name (e.g., "query" from "query = ...")
    # Group 3: argument value string (e.g., '"hello"' or '{"a": 1}')
    BUILTIN_CALL_REGEX_PATTERN: ta.ClassVar[re.Pattern[str]] = re.compile(
        r'<\|python_tag\|>\s*([^.(]+)\s*\.\s*call\s*\(\s*([\w]+)\s*=\s*([\s\S]*?)\s*\)',
        # Added optional whitespace \s* before the final parenthesis for robustness, which is common in such patterns.
        # The C++ version didn't have it, but it's a minor defensive addition. If strict adherence is needed, remove it.
    )

    def parse(
            self,
            input_str: str,
            with_builtin_tools: bool = False,
    ) -> ChatMsg:
        """
        Parses an input string that might represent a message from a Llama 3.1 model,
        potentially containing built-in tool calls or general JSON tool calls.

        Args:
            input_str: The input string to parse.
            with_builtin_tools: If True, attempts to parse a specific "<|python_tag|>tool.call(arg=value)" format first.

        Returns:
            A ChatMessage object.
        """
        # TODO: tighten & simplify the parser, don't accept leading text context.
        # (This TODO is from the original C++ code)

        if with_builtin_tools:
            # std::regex_match checks if the *entire* string matches.
            # re.fullmatch() is the Python equivalent.
            # Strip input to match C++ behavior potentially more closely if regex_match on unstripped input was implicit
            match = self.BUILTIN_CALL_REGEX_PATTERN.fullmatch(input_str.strip())
            if match:
                try:
                    name = match.group(1).strip()
                    arg_name = match.group(2).strip()
                    arg_value_str = match.group(3).strip()

                    # Parse the argument value string as JSON
                    # (std::string -> json -> C++ type)
                    # (str -> Python dict/list/str/int/etc.)
                    arg_value = json.loads(arg_value_str)

                    msg = ChatMsg()
                    tool_call_id = f'call_{name}_{arg_name}'  # Generating a simple ID

                    msg.tool_calls.append(ChatToolCall(
                        id=tool_call_id,  # Original C++ set this to ""
                        name=name,
                        # arguments must be a JSON string
                        arguments=json.dumps({arg_name: arg_value}),
                    ))
                    return msg

                except json.JSONDecodeError as e:
                    log.warning(
                        'Failed to parse builtin tool call arguments JSON (%s): %s',
                        str(e),
                        input_str,
                    )

                except Exception as e:  # noqa
                    log.warning(
                        'Failed to parse builtin tool call for other reasons (%s): %s',
                        str(e),
                        input_str,
                    )

            # If regex doesn't match or an exception occurred, fall through
            # to the generic JSON tool call parser.

        # Fallback to general JSON tool call parsing
        return parse_json_tool_calls(
            input_str,
            None,  # Corresponds to std::nullopt
            self.FUNCTION_REGEX_PATTERN,
            self.CLOSE_REGEX_PATTERN,
        )


##


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
