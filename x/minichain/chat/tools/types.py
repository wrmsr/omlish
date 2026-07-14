from omcore import dataclasses as dc
from omcore import lang

from ...tools.types import ToolSpec
from ..types import ChatOption


##


@dc.dataclass(frozen=True)
class Tool(ChatOption, lang.Final):
    spec: ToolSpec
