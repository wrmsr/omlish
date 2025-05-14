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

    raw_args: str | None = None


class ToolExecParser(lang.Abstract):
    @abc.abstractmethod
    def parse_tool_exec(self, s: str) -> list[ParsedToolExec] | None:
        raise NotImplementedError
