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

    id: str | None = None
    raw_args: str | None = None
    reasoning: str | None = None


@dc.dataclass(frozen=True)
class ParsedToolExecs:
    tool_execs: ta.Sequence[ParsedToolExec]

    _: dc.KW_ONLY

    stripped_text: str | None = None


class ToolExecParser(lang.Abstract):
    @abc.abstractmethod
    def parse_tool_execs(self, text: str) -> ParsedToolExecs | None:
        raise NotImplementedError
