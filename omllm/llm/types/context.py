import typing as ta

from omcore import dataclasses as dc

from .messages import Message
from .tools import Tool


##


@ta.final
@dc.dataclass(frozen=True, kw_only=True)
class Context:
    system_prompt: str | None = None

    messages: ta.Sequence[Message] = ()

    tools: ta.Sequence[Tool] = ()
