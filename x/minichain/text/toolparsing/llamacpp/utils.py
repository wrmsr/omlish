# @omlish-llm-author gemini-2.5-pro
import json
import re
import typing as ta

from omlish.logs import all as logs

from .types import ChatMsg
from .types import ChatToolCall


log = logs.get_module_logger(globals())


##


def parse_json_from_string(s: str, index: int) -> tuple[ta.Any | None, int]:
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


def parse_json_tool_calls(
        input_str: str,
        *,
        trigger_pat: re.Pattern | None = None,
        function_pat: re.Pattern = re.compile(r''),  # Must be provided if used
        close_pat: re.Pattern = re.compile(r''),  # Must be provided if used
        allow_raw_python: bool = False,
) -> ChatMsg:
    """
    Parses input assuming tool calls are marked by function_pat, contain JSON, and end with close_pat. An optional
    trigger_pat starts the process.

    Args:
        input_str: The string potentially containing tool calls.
        trigger_pat: Optional regex to find the start of the tool call section.
        function_pat: Regex with one capture group for the function name.
        close_pat: Regex marking the end of the tool call arguments.
        allow_raw_python: Special handling for raw python code blocks.

    Returns:
        A ChatMsg object with parsed content and tool calls.
    """

    result = ChatMsg()
    current_pos = 0
    end_pos = len(input_str)

    if trigger_pat:
        match = trigger_pat.search(input_str)
        if not match:
            result.content = input_str
            return result
        result.content = input_str[:match.start()]
        current_pos = match.end()
    else:
        result.content = ''  # Start with empty content if no trigger

    while current_pos < end_pos:
        # Find the next function call start
        func_match = function_pat.search(input_str, current_pos)
        if not func_match:
            # No more function calls found, append the rest
            result.content += input_str[current_pos:]
            break

        # Append content before this function call
        result.content += input_str[current_pos:func_match.start()]

        name = func_match.group(1)  # Assumes group 1 is the name
        parse_start_pos = func_match.end()  # Start looking for JSON after the name match

        # Try to parse JSON arguments
        arguments_obj, next_pos = parse_json_from_string(input_str, parse_start_pos)

        if arguments_obj is not None:
            # Successfully parsed JSON, now look for the closing pattern
            close_match = close_pat.search(input_str, next_pos)
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
            # close_pat isn't needed. NOTE: C++ version captures till end. This might need refinement depending on
            # exact expected format. Does 'python' have a closer? Assuming it consumes the rest of the string here.
            code_content = input_str[parse_start_pos:]
            arguments_obj = {'code': code_content}
            arguments_str = json.dumps(arguments_obj)
            result.tool_calls.append(ChatToolCall(name=name, arguments=arguments_str, id=''))
            current_pos = end_pos  # Consumed the rest
            break
        else:
            # Failed to parse JSON, and not the special python case. Treat the function pat match and subsequent text
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


##


_REASONING_PAT = re.compile(
    r'^\s*(?:<think>([\s\S]*?)</think>\s*)?([\s\S]*)$',
    re.DOTALL,
)


def handle_think_tag_prelude(
        input_str: str,
        rest_parser: ta.Callable[[str], ChatMsg],
        *,
        extract_reasoning: bool,
) -> ChatMsg:
    """Checks for <think>...</think> tags at the beginning of the input and processes the rest using rest_parser."""

    # Regex to capture optional <think> block and the rest of the content. Handles potential whitespace around tags.
    # DOTALL allows '.' to match newline characters.
    match = _REASONING_PAT.match(input_str)

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
