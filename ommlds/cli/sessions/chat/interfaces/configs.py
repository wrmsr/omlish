from omlish import dataclasses as dc
from omlish import lang


##


@dc.dataclass(frozen=True, kw_only=True)
class InterfaceConfig(lang.Abstract):
    enable_tools: bool = False
    dangerous_no_tool_confirmation: bool = False
