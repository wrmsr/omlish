from omlish import dataclasses as dc
from omlish import lang

from ..configs import ToolSetConfig


##


@dc.dataclass(frozen=True, kw_only=True)
class TodoToolSetConfig(ToolSetConfig, lang.Final):
    pass
