from omlish import dataclasses as dc
from omlish import lang

from ...chat.messages import ToolUseResultMessage
from ...tools.types import ToolUse
from ..events.types import Event


##


@dc.dataclass(frozen=True)
class ToolUseEvent(Event, lang.Final):
    use: ToolUse


@dc.dataclass(frozen=True)
class ToolUseResultEvent(Event, lang.Final):
    message: ToolUseResultMessage
