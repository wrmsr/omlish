# @omlish-llm-author gemini-2.5-pro
import re

from omlish.logs import all as logs

from .types import ChatMsg
from .utils import handle_think_tag_prelude
from .utils import parse_json_from_string
from .utils import process_tool_call


log = logs.get_module_logger(globals())


##


# Regex to find potential tool calls (JSON or function tags). Combined the variations into one regex with
# alternatives. Using non-capturing groups (?:...) where possible. DOTALL allows '.' to match newlines within
# arguments etc.
_OPEN_PAT = re.compile(
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


class Hermes2ProParser:
    def __init__(
            self,
            *,
            extract_reasoning: bool = False,
    ) -> None:
        super().__init__()

        self._extract_reasoning = extract_reasoning

    def _parse_inner(
            self,
            content_to_parse: str,
            *,
            pos_after_args: int,
            close_tag: str,
            block_end: str,
    ) -> int:
        # Check for closing tags (</function> and potential ```)
        remaining_str = content_to_parse[pos_after_args:]
        remaining_str_lstrip = remaining_str.lstrip()
        advance = len(remaining_str) - len(remaining_str_lstrip)
        pos_after_args += advance  # Account for stripped whitespace

        if close_tag:
            if content_to_parse.startswith(close_tag, pos_after_args):
                pos_after_args += len(close_tag)
            else:
                raise ValueError(f"Missing close tag '{close_tag}'")  # noqa

        remaining_str = content_to_parse[pos_after_args:]
        remaining_str_lstrip = remaining_str.lstrip()
        advance = len(remaining_str) - len(remaining_str_lstrip)
        pos_after_args += advance  # Account for stripped whitespace

        if block_end:
            if content_to_parse.startswith(block_end, pos_after_args):
                pos_after_args += len(block_end)
            else:
                raise ValueError(f"Missing block end '{block_end}'")  # noqa

        return pos_after_args

    def _parse(self, content_to_parse: str) -> ChatMsg:
        """Inner function to parse the content after <think> tags are handled."""

        msg = ChatMsg()
        current_pos = 0
        end_pos = len(content_to_parse)

        while current_pos < end_pos:
            # Search from the current position
            match = _OPEN_PAT.search(content_to_parse, current_pos)

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
            func_name1 = match.group(4)  # <function=...> name
            func_name2 = match.group(5)  # <function name="..."> name

            tool_call_processed = False
            next_parse_pos = -1  # Where to continue parsing after a successful tool call

            try:
                if json_candidate_text:
                    # Case 1: Looks like a JSON object possibly within tags
                    close_tag = f'</{open_tag[1:]}' if open_tag else ''

                    # Start parsing JSON from the beginning of group 3 relative to the match start
                    json_obj, json_end_idx_rel = parse_json_from_string(match.group(0), match.start(3) - match.start())
                    json_end_idx_abs = json_end_idx_rel + match.start()

                    # Check if it's a valid tool call structure
                    if (
                            isinstance(json_obj, dict) and
                            'name' in json_obj and
                            'arguments' in json_obj
                    ):
                        # Valid tool call found
                        msg.tool_calls.append(process_tool_call(json_obj))
                        tool_call_processed = True
                        next_parse_pos = self._parse_inner(
                            content_to_parse,
                            pos_after_args=json_end_idx_abs,
                            close_tag=close_tag,
                            block_end=block_end,
                        )

                elif func_name1 or func_name2:
                    # Case 2: Looks like a <function...> tag
                    function_name = func_name1 or func_name2
                    close_tag = '</function>'

                    # Arguments start at the beginning of group 6 relative to match start
                    args_start_idx_abs = match.start(6)
                    arguments_obj, args_end_idx_abs = parse_json_from_string(content_to_parse, args_start_idx_abs)

                    if arguments_obj is not None:
                        # Successfully parsed arguments
                        tool_data = {
                            'name': function_name,
                            'arguments': arguments_obj,
                        }
                        msg.tool_calls.append(process_tool_call(tool_data))
                        tool_call_processed = True
                        next_parse_pos = self._parse_inner(
                            content_to_parse,
                            pos_after_args=args_end_idx_abs,
                            close_tag=close_tag,
                            block_end=block_end,
                        )

                    # else: Failed to parse arguments JSON, treat whole match as content later

            except Exception as e:  # noqa
                # If parsing tool call or checking tags fails, treat block as content
                log.warning(
                    'Failed processing potential tool call: %r. Treating as content: %r',
                    e,
                    match.group(0),
                )
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

    def parse(self, input_str: str) -> ChatMsg:
        """
        Parses the Hermes 2 Pro format, handling <think> tags and various tool call syntaxes (JSON objects, <function>
        tags).
        """

        try:
            # First, handle the optional <think> prelude
            return handle_think_tag_prelude(
                input_str,
                self._parse,
                extract_reasoning=self._extract_reasoning,
            )

        except Exception:  # noqa
            log.exception('Failed to parse Hermes 2 Pro input: Input: %r', input_str)

            # Return a message with the original input as content on failure
            msg = ChatMsg(content=input_str)
            return msg
