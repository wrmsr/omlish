import json
import logging
import re

from .common import parse_json_tool_calls
from .types import ChatMsg
from .types import ChatToolCall


log = logging.getLogger(__name__)


##


# std::regex("\\s*\\{\\s*(?:\"type\"\\s*:\\s*\"function\"\\s*,\\s*)?\"name\"\\s*:\\s*\"([^\"]+)\"\\s*,\\s*\"parameters\"\\s*: ");  # noqa
FUNCTION_REGEX_PATTERN: re.Pattern[str] = re.compile(
    r'\s*\{\s*(?:"type"\s*:\s*"function"\s*,\s*)?"name"\s*:\s*"([^"]+)"\s*,\s*"parameters"\s*:\s*',
)

# static const std::regex close_regex("\\}\\s*");
CLOSE_REGEX_PATTERN: re.Pattern[str] = re.compile(r'\}\s*')

# std::regex("<\\|python_tag\\|>\\s*([^.(]+)\\s*\\.\\s*call\\s*\\(\\s*([\\w]+)\\s*=\\s*([\\s\\S]*?)\\)");
# Group 1: tool name (e.g., "my_tool" from "my_tool.call")
# Group 2: argument name (e.g., "query" from "query = ...")
# Group 3: argument value string (e.g., '"hello"' or '{"a": 1}')
BUILTIN_CALL_REGEX_PATTERN: re.Pattern[str] = re.compile(
    r'<\|python_tag\|>\s*([^.(]+)\s*\.\s*call\s*\(\s*([\w]+)\s*=\s*([\s\S]*?)\s*\)',
    # Added optional whitespace \s* before the final parenthesis for robustness, which is common in such patterns.
    # The C++ version didn't have it, but it's a minor defensive addition. If strict adherence is needed, remove it.
)


def parse_llama_3_1(
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
        match = BUILTIN_CALL_REGEX_PATTERN.fullmatch(input_str.strip())
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
        FUNCTION_REGEX_PATTERN,
        CLOSE_REGEX_PATTERN,
    )
