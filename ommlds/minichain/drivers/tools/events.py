from omlish import dataclasses as dc
from omlish import lang

from ...chat.messages import ToolUseResultMessage
from ..types import Event
from .execution import ToolUseExecution


##


@dc.dataclass(frozen=True)
class ToolUseEvent(Event, lang.Final):
    tue: ToolUseExecution


@dc.dataclass(frozen=True)
class ToolUseResultEvent(Event, lang.Final):
    tue: ToolUseExecution
    message: ToolUseResultMessage
