from omlish import dataclasses as dc
from omlish import lang

from ..tools import ToolSpec
from .types import ChatRequestOption


##


@dc.dataclass(frozen=True)
class Tool(ChatRequestOption, lang.Final):
    spec: ToolSpec
