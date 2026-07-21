import typing as ta

from omcore import dataclasses as dc

from .. import llm


##


type Message = llm.Message


##


@ta.final
@dc.dataclass(frozen=True, kw_only=True)
class Context:
    system_prompt: str | None = None

    messages: ta.Sequence[Message] | None = None
