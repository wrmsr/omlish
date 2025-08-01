import typing as ta

from omlish import check
from omlish.formats import json

from .base import ParsedToolExec
from .base import ParsedToolExecs
from .base import ToolExecParser


##


class DumbToolExecParser(ToolExecParser):
    DEFAULT_TOOL_NAME_KEY: ta.ClassVar[str] = 'name'
    DEFAULT_TOOL_ARGS_KEY: ta.ClassVar[str] = 'arguments'

    def __init__(
            self,
            open_tag: str,
            close_tag: str,
            *,
            tool_name_key: str | None = None,
            tool_args_key: str | None = None,
            strip_whitespace: bool = False,
    ) -> None:
        super().__init__()

        self._open_tag = check.non_empty_str(open_tag)
        self._close_tag = check.non_empty_str(close_tag)
        if tool_name_key is None:
            tool_name_key = self.DEFAULT_TOOL_NAME_KEY
        self._tool_name_key = check.non_empty_str(tool_name_key)
        if tool_args_key is None:
            tool_args_key = self.DEFAULT_TOOL_ARGS_KEY
        self._tool_args_key = check.non_empty_str(tool_args_key)
        self._strip_whitespace = strip_whitespace

    def parse_tool_execs(self, text: str) -> ParsedToolExecs | None:
        lst: list[str | ParsedToolExec] = []

        def append_str(s: str) -> None:
            if self._strip_whitespace:
                s = s.strip()
                if not s:
                    return
            lst.append(s)

        start_pos = 0
        while (open_pos := text.find(self._open_tag, start_pos)) >= 0:
            if start_pos != open_pos:
                append_str(text[start_pos:open_pos])

            body_open_pos = open_pos + len(self._open_tag)
            body_close_pos = text.index(self._close_tag, body_open_pos)

            close_pos = body_close_pos + len(self._close_tag)

            body = text[body_open_pos:body_close_pos]
            obj = json.loads(body.strip())

            lst.append(ParsedToolExec(
                check.non_empty_str(obj[self._tool_name_key]),
                check.isinstance(obj[self._tool_args_key], ta.Mapping),
                raw_text=text[open_pos:close_pos],
                raw_body=body,
            ))

            start_pos = close_pos

        if not lst:
            return None

        if start_pos != len(text):
            append_str(text[start_pos:])

        return lst
