import typing as ta

from omlish import dataclasses as dc
from omlish import lang


##


@dc.dataclass(frozen=True, kw_only=True)
class ToolsConfig:
    silent: bool = False
    dangerous_no_confirmation: bool = False
    enabled_tools: ta.Iterable[str] | None = None


##


@dc.dataclass(frozen=True, kw_only=True)
class ToolSetConfig(lang.Abstract):
    pass
