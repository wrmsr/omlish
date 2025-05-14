import abc

from omlish import lang

from ....tools import ToolExecRequest


##


class ToolParser(lang.Abstract):
    @abc.abstractmethod
    def parse_tool_exec_requests(self, s: str) -> list[ToolExecRequest] | None:
        raise NotImplementedError
