import typing as ta

from omlish import dataclasses as dc
from omlish import lang


##


@dc.dataclass(frozen=True, kw_only=True)
class ToolsConfig:
    enabled_tools: ta.Iterable[str] | None = None

    print_executions: bool = False


##


@dc.dataclass(frozen=True, kw_only=True)
class ToolSetConfig(lang.Abstract):
    pass
