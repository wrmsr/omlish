import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang


##


@dc.dataclass(frozen=True)
class ParsedToolExec:
    name: str
    args: ta.Mapping[str, ta.Any]

    _: dc.KW_ONLY

    raw_text: str | None = None
    raw_body: str | None = None

    id: str | None = None

    reasoning: str | None = None


ParsedToolExecs: ta.TypeAlias = ta.Sequence[str | ParsedToolExec]


class ToolExecParser(lang.Abstract):
    @abc.abstractmethod
    def parse_tool_execs(self, text: str) -> ParsedToolExecs | None:
        raise NotImplementedError

    @ta.final
    def parse_tool_execs_(self, text: str) -> ParsedToolExecs:
        if (pts := self.parse_tool_execs(text)) is not None:
            return pts
        else:
            return [text]
