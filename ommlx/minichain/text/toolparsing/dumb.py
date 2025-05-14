import io
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

    def parse_tool_execs(self, text: str) -> ParsedToolExecs | None:
        out: io.StringIO = io.StringIO()
        lst: list[ParsedToolExec] = []

        start_pos = 0
        while (open_pos := text.find(self._open_tag, start_pos)) >= 0:
            out.write(text[start_pos:open_pos])

            body_pos = open_pos + len(self._open_tag)
            close_pos = text.index(self._close_tag, body_pos)

            body = text[body_pos:close_pos]
            obj = json.loads(body.strip())

            lst.append(ParsedToolExec(
                check.non_empty_str(obj[self._tool_name_key]),
                check.isinstance(obj[self._tool_args_key], ta.Mapping),
                raw_args=body,
            ))

            start_pos = close_pos + len(self._close_tag)

        if not lst:
            return None

        out.write(text[start_pos:])

        return ParsedToolExecs(
            lst,
            stripped_text=out.getvalue(),
        )
